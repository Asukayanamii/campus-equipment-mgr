import uuid
import secrets
from datetime import datetime, timedelta

from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BussinessException
from app.core.logger import logger
from app.crud import user_crud
from app.db.models.user_model import User
import bcrypt
import jwt

from app.schema.common_schema import (
    EmailBindingIn,
    EmailLoginIn,
    EmailLoginOut,
    EmailVerificationCodeIn,
    GetMeOut,
    LoginIn,
    LoginOut,
    RegisterIn,
    UpdateIn,
)
from app.utils.mail_util import send_email_verification_code
from app.utils.redis_cache import get_redis_client

EMAIL_BINDING_VERIFICATION_CODE_KEY_PREFIX = "email:binding:"


def register_by_password(register_in: RegisterIn, db: Session):
    with db.begin():
        # 校验用户名在学生端是否已注册。
        user = user_crud.query_user_by_username(register_in.username, db)
        if user:
            raise BussinessException("用户已存在",status_code=409)
        # 加密密码并补齐系统生成的昵称、默认头像。
        salt = bcrypt.gensalt()
        register_in.password = bcrypt.hashpw(register_in.password.encode('utf-8'), salt).decode('utf-8')
        user = User(**register_in.model_dump())
        user.name = 'user'+ uuid.uuid5(uuid.NAMESPACE_DNS, register_in.username).hex[:5]
        user.image = settings.DEFAULT_PROFILE_IMAGE_URL
        # 在当前事务中保存学生账号。
        user_crud.add_user(user, db)
        return None


def login(login_in: LoginIn, db: Session):
    # 查询账号并校验密码哈希。
    user = user_crud.query_user_by_username(login_in.username, db)
    if not user or not bcrypt.checkpw(login_in.password.encode('utf-8'), user.password.encode('utf-8')):
        logger.info("用户名或密码错误")
        raise BussinessException("用户名或密码错误",status_code=401)
    # 按配置的有效期签发学生端 JWT。
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 加入过期时间字段 exp（JWT标准字段）
    token = jwt.encode({"username": user.username, 'id': user.id,'exp': expire}, settings.USER_JWT_SECRET_KEY,
                        algorithm=settings.ALGORITHM)
    return LoginOut(token=token, id=user.id, name=user.name,username=user.username)


def _generate_email_username(db: Session) -> str:
    """生成符合账号正则且未被占用的默认用户名。"""
    while True:
        username = f"email_{secrets.token_hex(6)}"
        if not user_crud.query_user_by_username(username, db):
            return username


def _build_email_binding_verification_code_key(email: str) -> str:
    """为邮箱绑定验证码生成独立 Redis 键，避免与登录验证码互通。"""
    return f"{EMAIL_BINDING_VERIFICATION_CODE_KEY_PREFIX}{email}"


async def send_email_verification_code_service(
    email_in: EmailVerificationCodeIn,
    redis_key: str | None = None,
) -> None:
    """生成验证码、写入 Redis，并通过 SMTP 发送给学生邮箱。"""
    verification_code_key = redis_key or email_in.email
    verification_code = f"{secrets.randbelow(1_000_000):06d}"
    encrypted_code = bcrypt.hashpw(
        verification_code.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")
    try:
        # 调用方传入独立键时可隔离不同业务的验证码，SET NX 防止有效期内重复发送。
        saved = get_redis_client().set(
            verification_code_key,
            encrypted_code,
            ex=settings.EMAIL_VERIFICATION_CODE_EXPIRE_SECONDS,
            nx=True,
        )
    except RedisError:
        logger.exception("邮箱验证码写入 Redis 失败")
        raise BussinessException("验证码服务暂不可用", status_code=503)
    if not saved:
        raise BussinessException("验证码已发送，请在有效期结束后再试", status_code=429)

    try:
        await send_email_verification_code(email_in.email, verification_code)
    except Exception:
        # 邮件发送失败时删除已写入的验证码，允许用户重新发起请求。
        get_redis_client().delete(verification_code_key)
        logger.exception("邮箱验证码发送失败")
        raise BussinessException("验证码发送失败", status_code=503)


def _verify_email_verification_code(
    email: str,
    verification_code: str,
    redis_key: str | None = None,
) -> None:
    """校验并消费指定邮箱的验证码，确保验证码只能使用一次。"""
    verification_code_key = redis_key or email
    try:
        encrypted_code = get_redis_client().get(verification_code_key)
    except RedisError:
        logger.exception("邮箱验证码读取 Redis 失败")
        raise BussinessException("验证码服务暂不可用", status_code=503)
    if not encrypted_code or not bcrypt.checkpw(
        verification_code.encode("utf-8"),
        encrypted_code.encode("utf-8"),
    ):
        raise BussinessException("验证码错误或已过期", status_code=400)

    try:
        get_redis_client().delete(verification_code_key)
    except RedisError:
        logger.exception("邮箱验证码删除 Redis 失败")
        raise BussinessException("验证码服务暂不可用", status_code=503)


async def send_email_binding_verification_code_service(
    email_in: EmailVerificationCodeIn,
    user_id: int,
    db: Session,
) -> None:
    """确认邮箱未被其他学生绑定后发送绑定验证码。"""
    user = user_crud.get_user_by_id(user_id, db)
    if not user:
        raise BussinessException("用户不存在", status_code=404)
    # 已绑定邮箱的账号不允许再次申请绑定验证码，避免绕过绑定限制。
    if user.email:
        raise BussinessException("当前账号已绑定邮箱，不能重复绑定", status_code=409)
    email_user = user_crud.query_user_by_email(email_in.email, db)
    if email_user and email_user.id != user_id:
        raise BussinessException("该邮箱已被其他学生绑定", status_code=409)
    await send_email_verification_code_service(
        email_in,
        _build_email_binding_verification_code_key(email_in.email),
    )


def bind_email_service(email_binding_in: EmailBindingIn, user_id: int, db: Session) -> None:
    """校验验证码后更新当前学生邮箱，普通资料更新不允许修改该字段。"""
    with db.begin():
        user = user_crud.get_user_by_id(user_id, db)
        if not user:
            raise BussinessException("用户不存在", status_code=404)
        # 先判断当前账号的绑定状态，重复绑定时不消费已经发送的验证码。
        if user.email:
            raise BussinessException("当前账号已绑定邮箱，不能重复绑定", status_code=409)
        _verify_email_verification_code(
            email_binding_in.email,
            email_binding_in.verification_code,
            _build_email_binding_verification_code_key(email_binding_in.email),
        )
        email_user = user_crud.query_user_by_email(email_binding_in.email, db)
        if email_user and email_user.id != user_id:
            raise BussinessException("该邮箱已被其他学生绑定", status_code=409)
        user_crud.update_user_email(user, email_binding_in.email, db)


def email_register_login_service(email_login_in: EmailLoginIn, db: Session) -> EmailLoginOut:
    """校验邮箱验证码，不存在账号时创建学生账号后签发 JWT。"""
    _verify_email_verification_code(email_login_in.email, email_login_in.verification_code)

    with db.begin():
        # 已注册用户直接登录；新用户仅由邮箱创建，其他资料使用系统默认值。
        user = user_crud.query_user_by_email(email_login_in.email, db)
        if not user:
            username = _generate_email_username(db)
            user = User(
                username=username,
                # 默认昵称与用户名密码注册保持相同的生成规则。
                name="user" + uuid.uuid5(uuid.NAMESPACE_DNS, username).hex[:5],
                image=settings.DEFAULT_PROFILE_IMAGE_URL,
                email=email_login_in.email,
            )
            user_crud.add_user(user, db)

        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = jwt.encode(
            {"id": user.id, "email": user.email, "exp": expire},
            settings.USER_JWT_SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return EmailLoginOut(
            id=user.id,
            name=user.name,
            username=user.username,
            image=user.image,
            email=user.email,
            token=token,
        )


def update_me(update_in: UpdateIn, db: Session) -> None:
    with db.begin():
        # 确认令牌对应的用户仍然存在。
        user = user_crud.get_user_by_id(update_in.id, db)
        if not user:
            raise BussinessException("用户不存在", status_code=404)
        update_model = User(**update_in.model_dump(exclude={"new_password"}))
        if update_in.password is not None:
            if not user.password or not bcrypt.checkpw(update_in.password.encode("utf-8"), user.password.encode("utf-8")):
                raise BussinessException("原密码错误", status_code=400)
            # 原密码仅用于校验，新密码才会被加密后持久化。
            salt = bcrypt.gensalt()
            update_model.password = bcrypt.hashpw(update_in.new_password.encode('utf-8'), salt).decode('utf-8')
        update_model.update_time = datetime.now()
        user_crud.update_user(update_model, db)


def get_me(id: int, db: Session) -> GetMeOut:
    # 查询当前用户并转换为对外响应模型。
    user = user_crud.get_user_by_id(id, db)
    return GetMeOut.model_validate(user)
        # 重新加密新密码并写入允许更新的个人信息。

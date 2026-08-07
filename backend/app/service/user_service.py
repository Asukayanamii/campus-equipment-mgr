import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BussinessException
from app.core.logger import logger
from app.crud import user_crud
from app.db.models.user_model import User
import bcrypt
import jwt

from app.schema.common_schema import GetMeOut, LoginIn, LoginOut, RegisterIn, UpdateIn


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


def update_me(update_in: UpdateIn, db: Session) -> None:
    with db.begin():
        # 确认令牌对应的用户仍然存在。
        user = user_crud.get_user_by_id(update_in.id, db)
        if not user:
            raise BussinessException("用户不存在", status_code=404)
        salt = bcrypt.gensalt()
        update_in.password = bcrypt.hashpw(update_in.password.encode('utf-8'), salt).decode('utf-8')
        update_model = User(**update_in.model_dump())
        update_model.update_time = datetime.now()
        user_crud.update_user(update_model, db)


def get_me(id: int, db: Session) -> GetMeOut:
    # 查询当前用户并转换为对外响应模型。
    user = user_crud.get_user_by_id(id, db)
    return GetMeOut.model_validate(user)
        # 重新加密新密码并写入允许更新的个人信息。

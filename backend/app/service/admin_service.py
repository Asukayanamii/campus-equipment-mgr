import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BussinessException
from app.core.logger import logger
from app.crud import admin_crud
from app.db.models.admin_model import Admin
import bcrypt
import jwt

from app.schema.common_schema import AdminRegisterIn, LoginIn, LoginOut, UpdateIn, GetMeOut


def register_by_password(register_in: AdminRegisterIn, db: Session) -> None:
    if register_in.registration_code != settings.ADMIN_REGISTRATION_CODE:
        raise BussinessException("管理员注册码错误", status_code=403)
    with db.begin():
        # 校验管理员用户名是否已注册。
        admin = admin_crud.query_admin_by_username(register_in.username, db)
        if admin:
            raise BussinessException("用户已存在", status_code=409)
        # 加密密码并补齐系统生成的昵称、默认头像。
        salt = bcrypt.gensalt()
        register_in.password = bcrypt.hashpw(register_in.password.encode('utf-8'), salt).decode('utf-8')
        admin = Admin(**register_in.model_dump(exclude={"registration_code"}))
        admin.name = 'admin'+ uuid.uuid5(uuid.NAMESPACE_DNS, register_in.username).hex[:5]
        admin.image = settings.DEFAULT_PROFILE_IMAGE_URL
        # 在当前事务中保存管理员账号。
        admin_crud.add_admin(admin, db)
        return None


def login(login_in: LoginIn, db: Session) -> LoginOut:
    # 查询管理员账号并校验密码哈希。
    admin = admin_crud.query_admin_by_username(login_in.username, db)
    if not admin or not bcrypt.checkpw(login_in.password.encode('utf-8'), admin.password.encode('utf-8')):
        logger.info("用户名或密码错误")
        raise BussinessException("用户名或密码错误", status_code=401)
    # 按配置的有效期签发管理员端 JWT。
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"username": admin.username, 'id': admin.id, 'exp': expire}, settings.ADMIN_JWT_SECRET_KEY,
                        algorithm=settings.ALGORITHM)
    return LoginOut(token=token, id=admin.id, name=admin.name, username=admin.username)


def update_me(update_in: UpdateIn, db: Session) -> None:
    with db.begin():
        # 确认令牌对应的管理员仍然存在。
        admin = admin_crud.get_admin_by_id(update_in.id,db)
        if not admin:
            raise BussinessException("用户不存在", status_code=404)
        salt = bcrypt.gensalt()
        update_in.password = bcrypt.hashpw(update_in.password.encode('utf-8'), salt).decode('utf-8')
        update_model = Admin(**update_in.model_dump())
        update_model.update_time = datetime.now()
        admin_crud.update_admin(update_model,db)


def get_me(id: int, db: Session) -> GetMeOut:
    # 查询当前管理员并转换为对外响应模型。
    admin = admin_crud.get_admin_by_id(id, db)
    me = GetMeOut.model_validate(admin)
    return me
        # 重新加密新密码并写入允许更新的个人信息。

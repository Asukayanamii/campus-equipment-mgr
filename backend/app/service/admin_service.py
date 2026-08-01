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

from app.schema.common_schema import LoginIn, LoginOut, RegisterIn, UpdateIn, GetMeOut


def register_by_password(register_in: RegisterIn, db: Session) -> None:
    with db.begin():
        # 判断用户是否存在
        admin = admin_crud.query_admin_by_username(register_in.username, db)
        if admin:
            raise BussinessException("用户已存在", status_code=409)
        # 密码加密存储
        salt = bcrypt.gensalt()
        register_in.password = bcrypt.hashpw(register_in.password.encode('utf-8'), salt).decode('utf-8')
        admin = Admin(**register_in.model_dump())
        admin.name = 'admin'+ uuid.uuid5(uuid.NAMESPACE_DNS, register_in.username).hex[:5]
        admin.image = settings.DEFAULT_PROFILE_IMAGE_URL
        admin_crud.add_admin(admin, db)
        return None


def login(login_in: LoginIn, db: Session) -> LoginOut:
    # 判断用户是否存在
    admin = admin_crud.query_admin_by_username(login_in.username, db)
    if not admin or not bcrypt.checkpw(login_in.password.encode('utf-8'), admin.password.encode('utf-8')):
        logger.info("用户名或密码错误")
        raise BussinessException("用户名或密码错误", status_code=401)
    # 发布token令牌
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"username": admin.username, 'id': admin.id, 'exp': expire}, settings.ADMIN_JWT_SECRET_KEY,
                        algorithm=settings.ALGORITHM)
    return LoginOut(token=token, id=admin.id, name=admin.name, username=admin.username)


def update_me(update_in: UpdateIn, db: Session) -> None:
    with db.begin():
        admin = admin_crud.get_admin_by_id(update_in.id,db)
        if not admin:
            raise BussinessException("用户不存在", status_code=404)
        salt = bcrypt.gensalt()
        update_in.password = bcrypt.hashpw(update_in.password.encode('utf-8'), salt).decode('utf-8')
        update_model = Admin(**update_in.model_dump())
        update_model.update_time = datetime.now()
        admin_crud.update_admin(update_model,db)


def get_me(id: int, db: Session) -> GetMeOut:
    admin = admin_crud.get_admin_by_id(id, db)
    me = GetMeOut.model_validate(admin)
    return me

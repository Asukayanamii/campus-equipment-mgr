from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BussinessException
from app.core.logger import logger
from app.crud import admin_crud
from app.db.models.admin_model import Admin
import bcrypt
import jwt

from app.schema.user_schema import LoginIn, LoginOut


def register_by_password(register_in, db: Session):
    # 判断用户是否存在
    admin = admin_crud.query_admin_by_username(register_in.username, db)
    if admin:
        raise BussinessException("用户已存在", status_code=409)
    admin = Admin(**register_in.model_dump())
    # 密码加密存储
    salt = bcrypt.gensalt()
    admin.password = bcrypt.hashpw(register_in.password.encode('utf-8'), salt)
    admin_crud.add_admin(admin, db)
    db.commit()
    return None


def login(login_in: LoginIn, db: Session):
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

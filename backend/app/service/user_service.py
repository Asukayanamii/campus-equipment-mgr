from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BussinessException
from app.core.logger import logger
from app.crud import user_crud
from app.db.models.user_model import User
import bcrypt
import jwt

from app.schema.user_schema import LoginIn, LoginOut


def register_by_password(register_in, db: Session):
    #判断用户是否存在
    user = user_crud.query_user_by_username(register_in.username, db)
    if user:
        raise BussinessException("用户已存在",status_code=409)
    user = User(**register_in.model_dump())
    #密码加密存储
    salt = bcrypt.gensalt()
    user.password = bcrypt.hashpw(register_in.password.encode('utf-8'), salt)
    user_crud.add_user(user, db)
    db.commit()
    return None


def login(login_in: LoginIn, db: Session):
    #判断用户是否存在
    user = user_crud.query_user_by_username(login_in.username, db)
    if not user or not bcrypt.checkpw(login_in.password.encode('utf-8'), user.password.encode('utf-8')):
        logger.info("用户名或密码错误")
        raise BussinessException("用户名或密码错误",status_code=401)
    #发布token令牌
    # 设置过期时间：当前时间 + ACCESS_TOKEN_EXPIRE_MINUTES分钟
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 加入过期时间字段 exp（JWT标准字段）
    token = jwt.encode({"username": user.username, 'id': user.id,'exp': expire}, settings.JWT_SECRET_KEY,
                        algorithm=settings.ALGORITHM)
    return LoginOut(token=token, id=user.id, name=user.name,username=user.username)
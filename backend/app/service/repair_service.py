from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BussinessException
from app.core.logger import logger
from app.crud import repair_user_crud
from app.db.models.repair_user_model import RepairUser
import bcrypt
import jwt

from app.schema.user_schema import LoginIn, LoginOut


def register_by_password(register_in, db: Session):
    # 判断用户是否存在
    repair_user = repair_user_crud.query_repair_user_by_username(register_in.username, db)
    if repair_user:
        raise BussinessException("用户已存在", status_code=409)
    repair_user = RepairUser(**register_in.model_dump())
    # 密码加密存储
    salt = bcrypt.gensalt()
    repair_user.password = bcrypt.hashpw(register_in.password.encode('utf-8'), salt)
    repair_user_crud.add_repair_user(repair_user, db)
    db.commit()
    return None


def login(login_in: LoginIn, db: Session):
    # 判断用户是否存在
    repair_user = repair_user_crud.query_repair_user_by_username(login_in.username, db)
    if not repair_user or not bcrypt.checkpw(login_in.password.encode('utf-8'), repair_user.password.encode('utf-8')):
        logger.info("用户名或密码错误")
        raise BussinessException("用户名或密码错误", status_code=401)
    # 发布token令牌
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"username": repair_user.username, 'id': repair_user.id, 'exp': expire}, settings.REPAIR_JWT_SECRET_KEY,
                        algorithm=settings.ALGORITHM)
    return LoginOut(token=token, id=repair_user.id, name=repair_user.name, username=repair_user.username)

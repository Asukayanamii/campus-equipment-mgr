from datetime import datetime, timedelta

import uuid
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BussinessException
from app.core.logger import logger
from app.crud import repair_user_crud
from app.db.models.repair_user_model import RepairUser
import bcrypt
import jwt

from app.schema.common_schema import GetMeOut, LoginIn, LoginOut, RegisterIn, UpdateIn


def register_by_password(register_in: RegisterIn, db: Session):
    with db.begin():
        # 判断用户是否存在
        repair_user = repair_user_crud.query_repair_user_by_username(register_in.username, db)
        if repair_user:
            raise BussinessException("用户已存在", status_code=409)
        # 密码加密存储
        salt = bcrypt.gensalt()
        register_in.password = bcrypt.hashpw(register_in.password.encode('utf-8'), salt)
        repair = RepairUser(**register_in.model_dump())
        repair.name = 'repair'+ uuid.uuid5(uuid.NAMESPACE_DNS, register_in.username).hex[:5]
        repair_user_crud.add_repair_user(repair, db)
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


def update_me(update_in: UpdateIn, db: Session) -> None:
    with db.begin():
        repair_user = repair_user_crud.get_repair_user_by_id(update_in.id, db)
        if not repair_user:
            raise BussinessException("用户不存在", status_code=404)
        salt = bcrypt.gensalt()
        update_in.password = bcrypt.hashpw(update_in.password.encode('utf-8'), salt)
        update_model = RepairUser(**update_in.model_dump())
        update_model.update_time = datetime.now()
        repair_user_crud.update_repair_user(update_model, db)


def get_me(id: int, db: Session) -> GetMeOut:
    repair_user = repair_user_crud.get_repair_user_by_id(id, db)
    return GetMeOut.model_validate(repair_user)

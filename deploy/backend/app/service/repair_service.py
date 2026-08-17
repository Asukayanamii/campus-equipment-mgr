from datetime import datetime, timedelta

import uuid
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BussinessException
from app.core.logger import logger
from app.crud import registration_code_crud, repair_user_crud
from app.db.models.repair_user_model import RepairUser
import bcrypt
import jwt

from app.schema.common_schema import GetMeOut, LoginIn, LoginOut, UpdateIn
from app.schema.repair_register_schema import RepairRegisterIn
from app.constant.status_constant import RegistrationCodeType


def register_by_password(register_in: RepairRegisterIn, db: Session):
    with db.begin():
        # 注册码与管理员注册共用同一张表，一经成功注册即不可再次使用。
        matched_code = registration_code_crud.get_unused_registration_code_by_code(
            db, register_in.registration_code, RegistrationCodeType.REPAIR
        )
        if not matched_code:
            raise BussinessException("注册码无效或已使用", status_code=400)
        # 校验维修人员用户名是否已注册。
        repair_user = repair_user_crud.query_repair_user_by_username(register_in.username, db)
        if repair_user:
            raise BussinessException("用户已存在", status_code=409)
        # 加密密码并补齐系统生成的昵称、默认头像。
        salt = bcrypt.gensalt()
        register_in.password = bcrypt.hashpw(register_in.password.encode('utf-8'), salt).decode('utf-8')
        repair = RepairUser(**register_in.model_dump(exclude={"registration_code"}))
        repair.name = 'repair'+ uuid.uuid5(uuid.NAMESPACE_DNS, register_in.username).hex[:5]
        repair.image = settings.DEFAULT_PROFILE_IMAGE_URL
        # 在当前事务中保存维修人员账号。
        repair_user_crud.add_repair_user(repair, db)
        # 账号保存成功后占用注册码，事务提交前任一步失败都会一并回滚。
        matched_code.is_used = True
        matched_code.update_time = datetime.now()
        return None


def login(login_in: LoginIn, db: Session):
    # 查询维修人员账号并校验密码哈希。
    repair_user = repair_user_crud.query_repair_user_by_username(login_in.username, db)
    if not repair_user or not bcrypt.checkpw(login_in.password.encode('utf-8'), repair_user.password.encode('utf-8')):
        logger.info("用户名或密码错误")
        raise BussinessException("用户名或密码错误", status_code=401)
    # 按配置的有效期签发维修端 JWT。
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"username": repair_user.username, 'id': repair_user.id, 'exp': expire}, settings.REPAIR_JWT_SECRET_KEY,
                        algorithm=settings.ALGORITHM)
    return LoginOut(token=token, id=repair_user.id, name=repair_user.name, username=repair_user.username)


def update_me(update_in: UpdateIn, db: Session) -> None:
    with db.begin():
        # 确认令牌对应的维修人员仍然存在。
        repair_user = repair_user_crud.get_repair_user_by_id(update_in.id, db)
        if not repair_user:
            raise BussinessException("用户不存在", status_code=404)
        update_model = RepairUser(**update_in.model_dump(exclude={"new_password"}))
        if update_in.password is not None:
            if not repair_user.password or not bcrypt.checkpw(update_in.password.encode("utf-8"), repair_user.password.encode("utf-8")):
                raise BussinessException("原密码错误", status_code=400)
            # 原密码仅用于校验，新密码才会被加密后持久化。
            salt = bcrypt.gensalt()
            update_model.password = bcrypt.hashpw(update_in.new_password.encode('utf-8'), salt).decode('utf-8')
        update_model.update_time = datetime.now()
        repair_user_crud.update_repair_user(update_model, db)


def get_me(id: int, db: Session) -> GetMeOut:
    # 查询当前维修人员并转换为对外响应模型。
    repair_user = repair_user_crud.get_repair_user_by_id(id, db)
    return GetMeOut.model_validate(repair_user)
        # 重新加密新密码并写入允许更新的个人信息。

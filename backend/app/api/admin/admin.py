from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.user_schema import RegisterIn, LoginIn, LoginOut
from app.service import admin_service

router = APIRouter(prefix="/admin", tags=["管理端"])


@router.post("/register", response_model=Result, name="管理员注册")
def register_by_password(register_in: RegisterIn, db: Session = Depends(get_db)):
    logger.info("管理端用户名密码注册")
    admin_service.register_by_password(register_in, db)
    return Result.success()


@router.post("/login", response_model=Result[LoginOut], name="管理员登录")
def login_by_password(login_in: LoginIn, db: Session = Depends(get_db)):
    logger.info("管理端用户名密码登录")
    login_out = admin_service.login(login_in, db)
    return Result.success(login_out)

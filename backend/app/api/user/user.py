from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import user_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.equipment_schema import EquipmentOut
from app.schema.page_schema import PageResp
from app.schema.common_schema import (
    EmailLoginIn,
    EmailLoginOut,
    EmailVerificationCodeIn,
    GetMeOut,
    LoginIn,
    LoginOut,
    RegisterIn,
    UpdateIn,
    UpdateInDTO,
)
from app.schema.equipment_schema import EquipQuery
from app.service import user_service

router = APIRouter(prefix="/user", tags=["学生端"])



@router.post("/register",response_model=Result,name="用户注册")
def register_by_password(register_in: RegisterIn,db: Session = Depends(get_db)):
    logger.info("学生端用户名密码注册")
    user_service.register_by_password(register_in,db)
    return Result.success()


@router.post("/login",response_model=Result[LoginOut],name="用户登录")
def login_by_password(login_in: LoginIn,db: Session = Depends(get_db)):
    logger.info("学生端用户名密码登录")
    login_out = user_service.login(login_in, db)
    return Result.success(login_out)


@router.post("/email-verification-code", response_model=Result, name="发送学生邮箱验证码")
async def send_email_verification_code(email_in: EmailVerificationCodeIn):
    logger.info("学生端发送邮箱验证码，邮箱：%s", email_in.email)
    await user_service.send_email_verification_code_service(email_in)
    return Result.success(message="验证码已发送")


@router.post("/email-login", response_model=Result[EmailLoginOut], name="学生邮箱验证码注册登录")
def email_register_login(email_login_in: EmailLoginIn, db: Session = Depends(get_db)):
    logger.info("学生端邮箱验证码注册登录，邮箱：%s", email_login_in.email)
    return Result.success(user_service.email_register_login_service(email_login_in, db))

@router.get("/me", response_model=Result[GetMeOut], name="鉴权，个人信息查询")
def me(db: Session = Depends(get_db), info: dict = Depends(user_verity)):
    logger.info("学生端鉴权，个人信息查询")
    return Result.success(user_service.get_me(info["id"], db))


@router.put("/update", response_model=Result, name="修改个人信息")
def update_me(
    update_in_dto: UpdateInDTO,
    info: dict = Depends(user_verity),
    db: Session = Depends(get_db),
):
    logger.info("修改个人信息")
    update_in = UpdateIn(**update_in_dto.model_dump(), id=info["id"])
    user_service.update_me(update_in, db)
    return Result.success()

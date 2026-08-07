from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import admin_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.common_schema import RegisterIn, LoginIn, LoginOut, UpdateIn, UpdateInDTO, GetMeOut
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

@router.get("/me",response_model=Result[GetMeOut],name="鉴权，个人信息查询",dependencies=[])
def me(db: Session = Depends(get_db),info: dict = Depends(admin_verity)):
    logger.info("管理端鉴权，个人信息查询")
    return Result.success(admin_service.get_me(info["id"],db))

@router.put("/update",response_model=Result,name="修改个人信息")
def update_me(update_in_DTO: UpdateInDTO,info: dict = Depends(admin_verity),db: Session = Depends(get_db)):
    logger.info("修改个人信息")
    update_in = UpdateIn(**update_in_DTO.model_dump(),id=info["id"])
    admin_service.update_me(update_in,db)
    return Result.success()

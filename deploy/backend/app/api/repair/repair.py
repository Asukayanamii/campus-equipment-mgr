from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import repair_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.common_schema import GetMeOut, LoginIn, LoginOut, UpdateIn, UpdateInDTO
from app.schema.repair_register_schema import RepairRegisterIn
from app.service import repair_service

router = APIRouter(prefix="/repair", tags=["维修端"])


@router.post("/register", response_model=Result, name="维修员注册")
def register_by_password(register_in: RepairRegisterIn, db: Session = Depends(get_db)):
    logger.info("维修端用户名密码注册")
    repair_service.register_by_password(register_in, db)
    return Result.success()


@router.post("/login", response_model=Result[LoginOut], name="维修员登录")
def login_by_password(login_in: LoginIn, db: Session = Depends(get_db)):
    logger.info("维修端用户名密码登录")
    login_out = repair_service.login(login_in, db)
    return Result.success(login_out)

@router.get("/me", response_model=Result[GetMeOut], name="鉴权，个人信息查询")
def me(db: Session = Depends(get_db), info: dict = Depends(repair_verity)):
    logger.info("维修端鉴权，个人信息查询")
    return Result.success(repair_service.get_me(info["id"], db))


@router.put("/update", response_model=Result, name="修改个人信息")
def update_me(
    update_in_dto: UpdateInDTO,
    info: dict = Depends(repair_verity),
    db: Session = Depends(get_db),
):
    logger.info("修改个人信息")
    update_in = UpdateIn(**update_in_dto.model_dump(), id=info["id"])
    repair_service.update_me(update_in, db)
    return Result.success()

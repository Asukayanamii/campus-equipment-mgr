from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.equipment_schema import EquipmentOut
from app.schema.page_schema import PageResp
from app.schema.user_schema import RegisterIn, LoginIn, LoginOut
from app.service.equipment_service import query_equipment, query_equipment_service
from app.schema.equipment_schema import EquipQuery
from app.service import user_service

router = APIRouter(prefix="/user", tags=["学生端"])



@router.post("/register",response_model=Result,name="用户注册")
def register_by_password(register_in: RegisterIn,db: Session = Depends(get_db)):
    logger.info("用户名密码注册")
    user_service.register_by_password(register_in,db)
    return Result.success()


@router.post("/login",response_model=Result[LoginOut],name="用户登录")
def login_by_password(login_in: LoginIn,db: Session = Depends(get_db)):
    logger.info("用户名密码登录")
    login_out = user_service.login(login_in, db)
    return Result.success(login_out)
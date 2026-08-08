from fastapi import APIRouter, Depends, Path, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import super_admin_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.registration_code_schema import (
    RegistrationCodeCreate,
    RegistrationCodeOut,
    RegistrationCodeQuery,
    RegistrationCodeUpdate,
)
from app.service.registration_code_service import (
    create_registration_code_service,
    delete_registration_code_service,
    query_registration_codes_service,
    update_registration_code_service,
)


router = APIRouter(
    prefix="/admin/registration-codes",
    tags=["管理端/注册码相关"],
    dependencies=[Depends(super_admin_verity)],
)


@router.get("/page", response_model=Result[Page[RegistrationCodeOut]], name="分页查询注册码")
def page_registration_codes(query: RegistrationCodeQuery = Query(), db: Session = Depends(get_db)):
    logger.info("管理端分页查询注册码")
    return Result.success(query_registration_codes_service(db, query))


@router.post("/", response_model=Result[RegistrationCodeOut], name="新增注册码")
def create_registration_code(code_in: RegistrationCodeCreate, db: Session = Depends(get_db)):
    logger.info("管理端新增注册码")
    return Result.success(create_registration_code_service(db, code_in))


@router.put("/{registrationCodeId}", response_model=Result, name="更新注册码")
def update_registration_code(
    code_in: RegistrationCodeUpdate,
    registration_code_id: int = Path(..., alias="registrationCodeId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端更新注册码，注册码 ID：%s", registration_code_id)
    update_registration_code_service(db, registration_code_id, code_in)
    return Result.success()


@router.delete("/{registrationCodeId}", response_model=Result, name="删除注册码")
def delete_registration_code(
    registration_code_id: int = Path(..., alias="registrationCodeId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端删除注册码，注册码 ID：%s", registration_code_id)
    delete_registration_code_service(db, registration_code_id)
    return Result.success()

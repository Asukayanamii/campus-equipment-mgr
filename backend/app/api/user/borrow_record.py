from fastapi import APIRouter, Depends, Path, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import user_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.borrow_record_schema import BorrowRecordCreate, BorrowRecordCreateOut, BorrowRecordOut, BorrowRecordPageOut, BorrowRecordQuery
from app.service.borrow_record_service import create_borrow_record_service, get_borrow_record_detail_by_user_service, query_borrow_record_by_user_service

router = APIRouter(prefix="/user/borrow-records", tags=["学生端/借用记录相关"], dependencies=[Depends(user_verity)])


@router.get("/page", response_model=Result[Page[BorrowRecordPageOut]], name="分页查询本人借用记录")
def page_borrow_records(
    query: BorrowRecordQuery = Query(),
    info: dict = Depends(user_verity),
    db: Session = Depends(get_db),
):
    logger.info("学生端分页查询本人借用记录")
    res = query_borrow_record_by_user_service(db, info["id"], query)
    return Result.success(res)


@router.get("/{borrowRecordId}", response_model=Result[BorrowRecordOut], name="查看本人借用记录详情")
def get_borrow_record_detail(
    borrow_record_id: int = Path(..., alias="borrowRecordId", ge=1),
    info: dict = Depends(user_verity),
    db: Session = Depends(get_db),
):
    logger.info("学生端查看本人借用记录详情，借用记录 ID：%s", borrow_record_id)
    res = get_borrow_record_detail_by_user_service(db, borrow_record_id, info["id"])
    return Result.success(res)


@router.post("", response_model=Result[BorrowRecordCreateOut], name="提交借用申请")
def create_borrow_record(
    borrow_record_in: BorrowRecordCreate,
    info: dict = Depends(user_verity),
    db: Session = Depends(get_db),
):
    logger.info("学生端提交借用申请，设备 ID：%s", borrow_record_in.equipment_id)
    borrow_record_out = create_borrow_record_service(db, info["id"], borrow_record_in)
    return Result.success(borrow_record_out)

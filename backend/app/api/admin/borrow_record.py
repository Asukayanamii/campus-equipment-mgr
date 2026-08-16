from fastapi import APIRouter, Depends, Path, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import admin_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.admin_borrow_record_schema import (
    AdminBorrowRecordOut,
    AdminBorrowRecordPageOut,
    AdminBorrowRecordQuery,
    BorrowRecordReview,
    BorrowRecordReviewOut,
)
from app.service.admin_borrow_record_service import (
    get_borrow_record_detail_by_admin_service,
    query_borrow_record_by_admin_service,
    review_borrow_record_service,
)

router = APIRouter(prefix="/admin/borrow-records", tags=["管理端/借用记录相关"], dependencies=[Depends(admin_verity)])


@router.get("/page", response_model=Result[Page[AdminBorrowRecordPageOut]], name="分页查询全部借用记录")
def page_borrow_records(
    query: AdminBorrowRecordQuery = Query(),
    db: Session = Depends(get_db),
):
    logger.info("管理端分页查询全部借用记录")
    return Result.success(query_borrow_record_by_admin_service(db, query))


@router.get("/{borrowRecordId}", response_model=Result[AdminBorrowRecordOut], name="查看借用记录详情")
def get_borrow_record_detail(
    borrow_record_id: int = Path(..., alias="borrowRecordId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端查看借用记录详情，借用记录 ID：%s", borrow_record_id)
    return Result.success(get_borrow_record_detail_by_admin_service(db, borrow_record_id))


@router.post("/{borrowRecordId}/review", response_model=Result[BorrowRecordReviewOut], name="审核借用申请")
def review_borrow_record(
    review_in: BorrowRecordReview,
    borrow_record_id: int = Path(..., alias="borrowRecordId", ge=1),
    info: dict = Depends(admin_verity),
    db: Session = Depends(get_db),
):
    logger.info("管理端审核借用申请，借用记录 ID：%s", borrow_record_id)
    return Result.success(review_borrow_record_service(db, borrow_record_id, info["id"], review_in))

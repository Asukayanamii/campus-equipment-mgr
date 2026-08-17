from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import admin_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.operation_log_schema import OperationLogOut, OperationLogQuery
from app.service.operation_log_service import query_operation_logs_service

router = APIRouter(
    prefix="/admin/operation-logs",
    tags=["管理端/操作日志相关"],
    dependencies=[Depends(admin_verity)],
)


@router.get("/page", response_model=Result[Page[OperationLogOut]], name="分页查询审核与状态变更记录")
def page_operation_logs(query: OperationLogQuery = Query(), db: Session = Depends(get_db)):
    # 管理员可按业务对象、设备和操作者审计全量操作记录。
    logger.info("管理端分页查询审核与状态变更记录")
    return Result.success(query_operation_logs_service(db, query))

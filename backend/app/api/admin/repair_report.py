from fastapi import APIRouter, Depends, Path, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import admin_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.repair_order_schema import (
    RepairReportAdminOut,
    RepairReportAdminPageOut,
    RepairReportConfirmOut,
)
from app.schema.repair_report_schema import RepairReportQuery
from app.service.repair_order_service import (
    confirm_repair_report_service,
    get_repair_report_by_admin_service,
    query_repair_reports_by_admin_service,
)

router = APIRouter(prefix="/admin/repair-reports", tags=["管理端/报修记录相关"], dependencies=[Depends(admin_verity)])


@router.get("/page", response_model=Result[Page[RepairReportAdminPageOut]], name="分页查询全部报修记录")
def page_repair_reports(query: RepairReportQuery = Query(), db: Session = Depends(get_db)):
    logger.info("管理端分页查询全部报修记录")
    return Result.success(query_repair_reports_by_admin_service(db, query))


@router.get("/{repairReportId}", response_model=Result[RepairReportAdminOut], name="查看报修记录详情")
def get_repair_report(
    repair_report_id: int = Path(..., alias="repairReportId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端查看报修记录详情，报修记录 ID：%s", repair_report_id)
    return Result.success(get_repair_report_by_admin_service(db, repair_report_id))


@router.post("/{repairReportId}/confirm", response_model=Result[RepairReportConfirmOut], name="确认报修记录")
def confirm_repair_report(
    repair_report_id: int = Path(..., alias="repairReportId", ge=1),
    info: dict = Depends(admin_verity),
    db: Session = Depends(get_db),
):
    logger.info("管理端确认报修记录，报修记录 ID：%s", repair_report_id)
    return Result.success(confirm_repair_report_service(db, repair_report_id, info["id"]))

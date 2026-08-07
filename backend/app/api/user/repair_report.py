from fastapi import APIRouter, Depends, Path, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import user_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.repair_report_schema import RepairReportOut, RepairReportPageOut, RepairReportQuery
from app.service.repair_report_service import get_repair_report_detail_by_user_service, query_repair_report_by_user_service

router = APIRouter(prefix="/user/repair-reports", tags=["学生端/报修记录相关"], dependencies=[Depends(user_verity)])


@router.get("/page", response_model=Result[Page[RepairReportPageOut]], name="分页查询本人报修记录")
def page_repair_reports(
    query: RepairReportQuery = Query(),
    info: dict = Depends(user_verity),
    db: Session = Depends(get_db),
):
    logger.info("学生端分页查询本人报修记录")
    res = query_repair_report_by_user_service(db, info["id"], query)
    return Result.success(res)


@router.get("/{repairReportId}", response_model=Result[RepairReportOut], name="查看本人报修记录详情")
def get_repair_report_detail(
    repair_report_id: int = Path(..., alias="repairReportId", ge=1),
    info: dict = Depends(user_verity),
    db: Session = Depends(get_db),
):
    logger.info("学生端查看本人报修记录详情，报修记录 ID：%s", repair_report_id)
    res = get_repair_report_detail_by_user_service(db, repair_report_id, info["id"])
    return Result.success(res)

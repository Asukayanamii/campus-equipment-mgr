from fastapi import APIRouter, Depends, Path, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import repair_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.repair_order_schema import (
    RepairOrderActionOut,
    RepairOrderCompletionIn,
    RepairOrderCompletionOut,
    RepairOrderOut,
    RepairOrderPageOut,
    RepairOrderQuery,
)
from app.service.repair_order_service import (
    accept_repair_order_service,
    complete_repair_order_service,
    get_repair_order_service,
    query_repair_orders_service,
    start_repair_order_service,
)

router = APIRouter(prefix="/repair/orders", tags=["维修端/维修工单相关"], dependencies=[Depends(repair_verity)])


@router.get("/page", response_model=Result[Page[RepairOrderPageOut]], name="分页查询本人维修工单")
def page_repair_orders(
    query: RepairOrderQuery = Query(),
    info: dict = Depends(repair_verity),
    db: Session = Depends(get_db),
):
    logger.info("维修端分页查询本人维修工单")
    return Result.success(query_repair_orders_service(db, query, info["id"]))


@router.get("/{repairOrderId}", response_model=Result[RepairOrderOut], name="查看本人维修工单详情")
def get_repair_order(
    repair_order_id: int = Path(..., alias="repairOrderId", ge=1),
    info: dict = Depends(repair_verity),
    db: Session = Depends(get_db),
):
    logger.info("维修端查看本人维修工单详情，工单 ID：%s", repair_order_id)
    return Result.success(get_repair_order_service(db, repair_order_id, info["id"]))


@router.post("/{repairOrderId}/accept", response_model=Result[RepairOrderActionOut], name="接收维修工单")
def accept_repair_order(
    repair_order_id: int = Path(..., alias="repairOrderId", ge=1),
    info: dict = Depends(repair_verity),
    db: Session = Depends(get_db),
):
    logger.info("维修端接收维修工单，工单 ID：%s", repair_order_id)
    return Result.success(accept_repair_order_service(db, repair_order_id, info["id"]))


@router.post("/{repairOrderId}/start", response_model=Result[RepairOrderActionOut], name="开始维修工单")
def start_repair_order(
    repair_order_id: int = Path(..., alias="repairOrderId", ge=1),
    info: dict = Depends(repair_verity),
    db: Session = Depends(get_db),
):
    logger.info("维修端开始维修工单，工单 ID：%s", repair_order_id)
    return Result.success(start_repair_order_service(db, repair_order_id, info["id"]))


@router.post("/{repairOrderId}/completion", response_model=Result[RepairOrderCompletionOut], name="提交维修结果")
def complete_repair_order(
    completion_in: RepairOrderCompletionIn,
    repair_order_id: int = Path(..., alias="repairOrderId", ge=1),
    info: dict = Depends(repair_verity),
    db: Session = Depends(get_db),
):
    logger.info("维修端提交维修结果，工单 ID：%s", repair_order_id)
    return Result.success(complete_repair_order_service(db, repair_order_id, info["id"], completion_in))

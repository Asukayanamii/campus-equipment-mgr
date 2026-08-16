from fastapi import APIRouter, Depends, Path, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import admin_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.common_schema import PageQuery
from app.schema.repair_order_schema import (
    RepairOrderActionOut,
    RepairOrderAssignIn,
    RepairOrderAssignOut,
    RepairOrderOut,
    RepairOrderPageOut,
    RepairOrderQuery,
    RepairUserPageOut,
)
from app.service.repair_order_service import (
    assign_repair_order_service,
    confirm_completed_repair_order_service,
    get_repair_order_service,
    query_repair_orders_service,
    query_repair_users_service,
    scrap_repair_order_service,
)

router = APIRouter(prefix="/admin/repair-orders", tags=["管理端/维修工单相关"], dependencies=[Depends(admin_verity)])
repair_user_router = APIRouter(prefix="/admin/repair-users", tags=["管理端/维修人员相关"], dependencies=[Depends(admin_verity)])


@router.get("/page", response_model=Result[Page[RepairOrderPageOut]], name="分页查询全部维修工单")
def page_repair_orders(query: RepairOrderQuery = Query(), db: Session = Depends(get_db)):
    logger.info("管理端分页查询全部维修工单")
    return Result.success(query_repair_orders_service(db, query))


@repair_user_router.get("/page", response_model=Result[Page[RepairUserPageOut]], name="分页查询维修人员")
def page_repair_users(query: PageQuery = Query(), db: Session = Depends(get_db)):
    logger.info("管理端分页查询维修人员")
    return Result.success(query_repair_users_service(db, query))


@router.get("/{repairOrderId}", response_model=Result[RepairOrderOut], name="查看维修工单详情")
def get_repair_order(
    repair_order_id: int = Path(..., alias="repairOrderId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端查看维修工单详情，工单 ID：%s", repair_order_id)
    return Result.success(get_repair_order_service(db, repair_order_id))


@router.post("/{repairOrderId}/assign", response_model=Result[RepairOrderAssignOut], name="派发维修工单")
def assign_repair_order(
    assign_in: RepairOrderAssignIn,
    repair_order_id: int = Path(..., alias="repairOrderId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端派发维修工单，工单 ID：%s", repair_order_id)
    return Result.success(assign_repair_order_service(db, repair_order_id, assign_in))


@router.post("/{repairOrderId}/confirm", response_model=Result[RepairOrderActionOut], name="确认维修完成")
def confirm_repair_order(
    repair_order_id: int = Path(..., alias="repairOrderId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端确认维修完成，工单 ID：%s", repair_order_id)
    return Result.success(confirm_completed_repair_order_service(db, repair_order_id))


@router.post("/{repairOrderId}/scrap", response_model=Result[RepairOrderActionOut], name="报废维修工单设备")
def scrap_repair_order(
    repair_order_id: int = Path(..., alias="repairOrderId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端报废维修工单设备，工单 ID：%s", repair_order_id)
    return Result.success(scrap_repair_order_service(db, repair_order_id))

from fastapi import APIRouter, Depends, Path, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import admin_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.equipment_schema import EquipmentCreate, EquipmentOut, EquipmentUpdate, EquipQuery
from app.service.equipment_service import (
    create_equipment_service,
    delete_equipment_service,
    get_equipment_service,
    query_equipment_service,
    update_equipment_service,
)

router = APIRouter(prefix="/admin/equipment", tags=["管理端/设备相关"], dependencies=[Depends(admin_verity)])


@router.get("/page", response_model=Result[Page[EquipmentOut]], name="分页条件查询设备")
def page_equipments(query: EquipQuery = Query(), db: Session = Depends(get_db)):
    logger.info("分页条件查询设备")
    res = query_equipment_service(db, query)
    return Result.success(res)


@router.get("/{equipmentId}", response_model=Result[EquipmentOut], name="根据 ID 查询设备详情")
def get_equipment(
    equipment_id: int = Path(..., alias="equipmentId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端根据 ID 查询设备详情，设备 ID：%s", equipment_id)
    return Result.success(get_equipment_service(db, equipment_id))


@router.post("", response_model=Result, name="新增设备")
def create_equipment(
    equipment_in: EquipmentCreate,
    info: dict = Depends(admin_verity),
    db: Session = Depends(get_db),
):
    logger.info("管理端新增设备，设备编号：%s", equipment_in.equipment_no)
    create_equipment_service(db, equipment_in, info["id"])
    return Result.success()


@router.put("/{equipmentId}", response_model=Result, name="根据 ID 更新设备")
def update_equipment(
    equipment_in: EquipmentUpdate,
    equipment_id: int = Path(..., alias="equipmentId", ge=1),
    info: dict = Depends(admin_verity),
    db: Session = Depends(get_db),
):
    logger.info("管理端根据 ID 更新设备，设备 ID：%s", equipment_id)
    update_equipment_service(db, equipment_id, equipment_in, info["id"])
    return Result.success()


@router.delete("/{equipmentId}", response_model=Result, name="根据 ID 删除设备")
def delete_equipment(
    equipment_id: int = Path(..., alias="equipmentId", ge=1),
    info: dict = Depends(admin_verity),
    db: Session = Depends(get_db),
):
    logger.info("管理端根据 ID 删除设备，设备 ID：%s", equipment_id)
    delete_equipment_service(db, equipment_id, info["id"])
    return Result.success()

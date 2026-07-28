from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import admin_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.equipment_schema import EquipmentOut, EquipQuery
from app.service.equipment_service import query_equipment_service

router = APIRouter(prefix="/admin/equipment", tags=["管理端"], dependencies=[Depends(admin_verity)])


@router.get("/page", response_model=Result[Page[EquipmentOut]], name="分页条件查询设备")
def page_equipments(query: EquipQuery = Query(), db: Session = Depends(get_db)):
    logger.info("分页条件查询设备")
    res = query_equipment_service(db, query)
    return Result.success(res)

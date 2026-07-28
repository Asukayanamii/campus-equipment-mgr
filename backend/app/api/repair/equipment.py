from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import repair_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.equipment_schema import EquipmentOut, EquipQuery
from app.service.equipment_service import query_equipment_service

router = APIRouter(prefix="/repair/equipment", tags=["维修端"], dependencies=[Depends(repair_verity)])


@router.get("/page", response_model=Result[Page[EquipmentOut]], name="分页条件查询设备")
def page_equipments(query: EquipQuery = Query(), db: Session = Depends(get_db)):
    logger.info("分页条件查询设备")
    res = query_equipment_service(db, query)
    return Result.success(res)

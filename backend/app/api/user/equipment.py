from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.equipment_schema import EquipmentOut
from app.schema.page_schema import PageResp
from app.schema.user_schema import RegisterIn
from app.service.equipment_service import query_equipment, query_equipment_service
from app.schema.equipment_schema import EquipQuery

router = APIRouter(prefix="/user/equipment", tags=["学生端"])

# @router.get("/equipments",response_model=Result[PageResp[EquipmentOut]],name="获取所有设备")
# def all_equipments(db: Session = Depends(get_db)):
#     logger.info("获取所有设备")
#     all_list = get_all_equipment(db)
#     return Result.success(all_list)

@router.get("/page",response_model=Result[Page[EquipmentOut]],name="分页条件查询设备")
def page_equipments(query: EquipQuery = Query(),db: Session = Depends(get_db)):
    logger.info("分页条件查询设备")
    res = query_equipment_service(db, query)
    return Result.success(res)

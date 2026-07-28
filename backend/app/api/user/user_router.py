from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.equipment_schema import EquipmentOut
from app.schema.page_schema import PageResp
from app.service.equipment_service import get_all_equipment

router = APIRouter(prefix="/user", tags=["用户端"])


@router.get("/equipments",response_model=Result[PageResp[EquipmentOut]])
def all_equipments(db: Session = Depends(get_db)):
    logger.info("获取所有设备")
    all_list = get_all_equipment(db)
    return Result.success(all_list)

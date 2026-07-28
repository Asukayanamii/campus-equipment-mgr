from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.equipment_category_model import EquipmentCategory


def get_category_by_id(session:Session,id:int) -> EquipmentCategory | None:
    stmt = select(EquipmentCategory).where(EquipmentCategory.id == id)
    return session.scalar(stmt)
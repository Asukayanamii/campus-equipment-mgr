from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.equipment_category_model import EquipmentCategory
from app.db.models.equipment_model import Equipment


def get_equipment_by_id(session:Session,id:int) -> Equipment | None:
    stmt = select(Equipment).where(Equipment.id == id)
    return session.scalar(stmt)

def list_all_equipment(session:Session) -> list[Equipment]:
    stmt = select(Equipment)
    return session.scalars(stmt).all()

def get_all_equipment_out(session:Session) -> list[tuple[Equipment,EquipmentCategory]]:
    stmt = select(Equipment,EquipmentCategory).outerjoin(EquipmentCategory,Equipment.category_id==EquipmentCategory.id)
    return session.execute(stmt).all()


if __name__=="__main__":
    from app.db.session import SessionLocal
    session = SessionLocal()
    print(list_all_equipment(session))
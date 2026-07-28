from fastapi_pagination import  Page
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, asc
from fastapi_pagination.ext.sqlalchemy import paginate
from app.db.models.equipment_category_model import EquipmentCategory
from app.db.models.equipment_model import Equipment
from app.schema.equipment_schema import EquipQuery


def get_equipment_by_id(session:Session,id:int) -> Equipment | None:
    stmt = select(Equipment).where(Equipment.id == id)
    return session.scalar(stmt)

def list_all_equipment(session:Session) -> list[Equipment]:
    stmt = select(Equipment)
    return session.scalars(stmt).all()

def get_all_equipment_out(session:Session) -> list[tuple[Equipment,EquipmentCategory]]:
    stmt = (select(Equipment,EquipmentCategory)
            .outerjoin(EquipmentCategory,Equipment.category_id==EquipmentCategory.id))
    return session.execute(stmt).all()

def query_equipment(session:Session,query:EquipQuery) -> Page[tuple[Equipment, EquipmentCategory]]:
    stmt = (select(Equipment,EquipmentCategory)
            .outerjoin(EquipmentCategory,Equipment.category_id==EquipmentCategory.id))
    if query.category_id:
        stmt = stmt.where(Equipment.category_id==query.category_id)
    if query.status:
        stmt = stmt.where(Equipment.status==query.status)
    if query.equipment_name:
        stmt = stmt.where(Equipment.equipment_name.like(f"%{query.equipment_name}%"))
    if query.equipment_no:
        stmt = stmt.where(Equipment.equipment_no.like(f"%{query.equipment_no}%"))
    if query.location:
        stmt = stmt.where(Equipment.location.like(f"%{query.location}%"))
    if query.brand:
        stmt = stmt.where(Equipment.brand.like(f"%{query.brand}%"))
    if query.spec:
        stmt = stmt.where(Equipment.spec.like(f"%{query.spec}%"))
    if query.start_time and query.end_time:
        stmt = stmt.where(Equipment.purchase_date.between(query.start_time,query.end_time))
    if query.sort and query.order:
        stmt = stmt.order_by(desc(getattr(Equipment,query.sort)) if query.order == "desc" else asc(getattr(Equipment,query.sort)))
    return paginate(session,stmt,query)


if __name__=="__main__":
    from app.db.session import SessionLocal
    session = SessionLocal()
    print(list_all_equipment(session))
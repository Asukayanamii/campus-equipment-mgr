from fastapi_pagination import  Page
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, asc
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic.alias_generators import to_snake
from app.db.models.equipment_category_model import EquipmentCategory
from app.db.models.equipment_model import Equipment
from app.schema.equipment_schema import EquipQuery


def get_equipment_by_id(session:Session,id:int) -> Equipment | None:
    stmt = select(Equipment).where(Equipment.id == id, Equipment.is_deleted == 0)
    return session.scalar(stmt)


def get_equipment_detail_by_id(session: Session, id: int) -> tuple[Equipment, EquipmentCategory | None] | None:
    stmt = (
        select(Equipment, EquipmentCategory)
        .outerjoin(EquipmentCategory, Equipment.category_id == EquipmentCategory.id)
        .where(Equipment.id == id, Equipment.is_deleted == 0)
    )
    return session.execute(stmt).one_or_none()


def get_equipment_by_no(session: Session, equipment_no: str) -> Equipment | None:
    stmt = select(Equipment).where(Equipment.equipment_no == equipment_no)
    return session.scalar(stmt)


def add_equipment(equipment: Equipment, session: Session) -> None:
    session.add(equipment)
    session.flush()


def update_equipment(equipment: Equipment, values: dict, session: Session) -> None:
    for field, value in values.items():
        setattr(equipment, field, value)
    session.flush()


def delete_equipment(equipment: Equipment, session: Session) -> None:
    equipment.is_deleted = 1
    session.flush()

def list_all_equipment(session:Session) -> list[Equipment]:
    stmt = select(Equipment).where(Equipment.is_deleted == 0)
    return session.scalars(stmt).all()

# def get_all_equipment_out(session:Session) -> list[tuple[Equipment,EquipmentCategory]]:
#     stmt = (select(Equipment,EquipmentCategory)
#             .outerjoin(EquipmentCategory,Equipment.category_id==EquipmentCategory.id))
#     return session.execute(stmt).all()

def query_equipment(session:Session,query:EquipQuery) -> Page[tuple[Equipment, EquipmentCategory]]:
    #拼接查询语句
    stmt = (select(Equipment,EquipmentCategory)
            .outerjoin(EquipmentCategory,Equipment.category_id==EquipmentCategory.id)
            .where(Equipment.is_deleted == 0))
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
    if query.sort or query.order:
        sort_column = getattr(Equipment, to_snake(query.sort or "id"))
        stmt = stmt.order_by(desc(sort_column) if query.order == "desc" else asc(sort_column))
    # paginate自动分页查询
    return paginate(session,stmt,query)


if __name__=="__main__":
    from app.db.session import SessionLocal
    session = SessionLocal()
    print(list_all_equipment(session))

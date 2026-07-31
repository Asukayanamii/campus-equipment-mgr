from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic.alias_generators import to_snake
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.db.models.equipment_category_model import EquipmentCategory
from app.schema.equipment_category_schema import CategoryQuery


def get_category_by_id(session:Session,id:int) -> EquipmentCategory | None:
    stmt = select(EquipmentCategory).where(
        EquipmentCategory.id == id,
        EquipmentCategory.is_deleted == 0,
    )
    return session.scalar(stmt)


def get_category_by_name(session: Session, category_name: str) -> EquipmentCategory | None:
    stmt = select(EquipmentCategory).where(EquipmentCategory.category_name == category_name)
    return session.scalar(stmt)


def query_categories(session: Session, query: CategoryQuery) -> Page[EquipmentCategory]:
    stmt = select(EquipmentCategory).where(EquipmentCategory.is_deleted == 0)
    if query.id:
        stmt = stmt.where(EquipmentCategory.id == query.id)
    if query.category_name:
        stmt = stmt.where(EquipmentCategory.category_name.like(f"%{query.category_name}%"))

    sort_field = to_snake(query.sort or "sort")
    sort_column = getattr(EquipmentCategory, sort_field, EquipmentCategory.sort)
    stmt = stmt.order_by(desc(sort_column) if query.order == "desc" else asc(sort_column))
    return paginate(session, stmt, query)


def add_category(category: EquipmentCategory, session: Session) -> None:
    session.add(category)
    session.flush()


def update_category(category: EquipmentCategory, values: dict, session: Session) -> None:
    for field, value in values.items():
        setattr(category, field, value)
    session.flush()


def delete_category(category: EquipmentCategory, session: Session) -> None:
    category.is_deleted = 1
    session.flush()

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.db.models.equipment_model import Equipment
from app.db.models.repair_order_image_model import RepairOrderImage
from app.db.models.repair_order_model import RepairOrder
from app.db.models.repair_report_model import RepairReport
from app.db.models.repair_user_model import RepairUser
from app.db.models.user_model import User
from app.schema.repair_order_schema import RepairOrderQuery


def add_repair_order(repair_order: RepairOrder, session: Session) -> None:
    session.add(repair_order)
    session.flush()


def get_repair_order_by_repair_report_id(session: Session, repair_report_id: int) -> RepairOrder | None:
    stmt = select(RepairOrder).where(RepairOrder.repair_report_id == repair_report_id)
    return session.scalar(stmt)


def update_repair_order(repair_order: RepairOrder, values: dict, session: Session) -> None:
    for field, value in values.items():
        setattr(repair_order, field, value)
    session.flush()


def get_repair_order_by_id_for_update(session: Session, repair_order_id: int) -> RepairOrder | None:
    stmt = select(RepairOrder).where(RepairOrder.id == repair_order_id).with_for_update()
    return session.scalar(stmt)


def query_repair_orders(
    session: Session,
    query: RepairOrderQuery,
    repair_user_id: int | None = None,
) -> Page[tuple[RepairOrder, Equipment | None, RepairUser | None]]:
    stmt = (
        select(RepairOrder, Equipment, RepairUser)
        .outerjoin(Equipment, RepairOrder.equipment_id == Equipment.id)
        .outerjoin(RepairUser, RepairOrder.repair_user_id == RepairUser.id)
    )
    if repair_user_id is not None:
        stmt = stmt.where(RepairOrder.repair_user_id == repair_user_id)
    if query.repair_user_id:
        stmt = stmt.where(RepairOrder.repair_user_id == query.repair_user_id)
    if query.status:
        stmt = stmt.where(RepairOrder.status == query.status)
    if query.equipment_name:
        stmt = stmt.where(Equipment.equipment_name.like(f"%{query.equipment_name}%"))
    stmt = stmt.order_by(desc(RepairOrder.create_time))
    return paginate(session, stmt, query)


def get_repair_order_detail(session: Session, repair_order_id: int):
    stmt = (
        select(RepairOrder, RepairReport, Equipment, User, RepairUser)
        .outerjoin(RepairReport, RepairOrder.repair_report_id == RepairReport.id)
        .outerjoin(Equipment, RepairOrder.equipment_id == Equipment.id)
        .outerjoin(User, RepairReport.user_id == User.id)
        .outerjoin(RepairUser, RepairOrder.repair_user_id == RepairUser.id)
        .where(RepairOrder.id == repair_order_id)
    )
    return session.execute(stmt).one_or_none()


def add_repair_order_image(image: RepairOrderImage, session: Session) -> None:
    session.add(image)
    session.flush()


def get_repair_order_images(session: Session, repair_order_id: int) -> list[RepairOrderImage]:
    stmt = (
        select(RepairOrderImage)
        .where(RepairOrderImage.repair_order_id == repair_order_id)
        .order_by(asc(RepairOrderImage.image_type), asc(RepairOrderImage.sort), asc(RepairOrderImage.id))
    )
    return session.scalars(stmt).all()

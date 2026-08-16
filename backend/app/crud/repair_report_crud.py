from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic.alias_generators import to_snake
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.db.models.repair_report_model import RepairReport
from app.db.models.equipment_category_model import EquipmentCategory
from app.db.models.equipment_model import Equipment
from app.db.models.repair_order_model import RepairOrder
from app.db.models.user_model import User
from app.schema.repair_report_schema import RepairReportQuery


def add_repair_report(repair_report: RepairReport, session: Session) -> None:
    session.add(repair_report)
    session.flush()


def get_repair_report_by_return_record_id(session: Session, return_record_id: int) -> RepairReport | None:
    stmt = select(RepairReport).where(RepairReport.return_record_id == return_record_id)
    return session.scalar(stmt)


def update_repair_report(repair_report: RepairReport, values: dict, session: Session) -> None:
    for field, value in values.items():
        setattr(repair_report, field, value)
    session.flush()


def get_repair_report_by_id_for_update(session: Session, repair_report_id: int) -> RepairReport | None:
    stmt = select(RepairReport).where(RepairReport.id == repair_report_id).with_for_update()
    return session.scalar(stmt)


def query_repair_reports_by_admin(session: Session, query: RepairReportQuery):
    stmt = (
        select(RepairReport, User, Equipment, RepairOrder)
        .outerjoin(User, RepairReport.user_id == User.id)
        .outerjoin(Equipment, RepairReport.equipment_id == Equipment.id)
        .outerjoin(RepairOrder, RepairReport.id == RepairOrder.repair_report_id)
    )
    if query.status:
        stmt = stmt.where(RepairReport.status == query.status)
    if query.equipment_name:
        stmt = stmt.where(Equipment.equipment_name.like(f"%{query.equipment_name}%"))
    stmt = stmt.order_by(desc(RepairReport.create_time))
    return paginate(session, stmt, query)


def get_repair_report_detail_by_id(session: Session, repair_report_id: int):
    stmt = (
        select(RepairReport, User, Equipment, RepairOrder)
        .outerjoin(User, RepairReport.user_id == User.id)
        .outerjoin(Equipment, RepairReport.equipment_id == Equipment.id)
        .outerjoin(RepairOrder, RepairReport.id == RepairOrder.repair_report_id)
        .where(RepairReport.id == repair_report_id)
    )
    return session.execute(stmt).one_or_none()


def query_repair_report_by_user(
    session: Session,
    user_id: int,
    query: RepairReportQuery,
) -> Page[tuple[RepairReport, Equipment | None]]:
    stmt = (
        select(RepairReport, Equipment)
        .outerjoin(Equipment, RepairReport.equipment_id == Equipment.id)
        .where(RepairReport.user_id == user_id)
    )
    if query.status:
        stmt = stmt.where(RepairReport.status == query.status)
    if query.equipment_name:
        stmt = stmt.where(Equipment.equipment_name.like(f"%{query.equipment_name}%"))
    if query.sort or query.order:
        sort_column = getattr(RepairReport, to_snake(query.sort or "id"))
        stmt = stmt.order_by(desc(sort_column) if query.order == "desc" else asc(sort_column))
    return paginate(session, stmt, query)


def get_repair_report_detail_by_id_and_user(
    session: Session,
    repair_report_id: int,
    user_id: int,
) -> tuple[RepairReport, Equipment | None, EquipmentCategory | None, RepairOrder | None] | None:
    stmt = (
        select(RepairReport, Equipment, EquipmentCategory, RepairOrder)
        .outerjoin(Equipment, RepairReport.equipment_id == Equipment.id)
        .outerjoin(EquipmentCategory, Equipment.category_id == EquipmentCategory.id)
        .outerjoin(RepairOrder, RepairReport.id == RepairOrder.repair_report_id)
        .where(
            RepairReport.id == repair_report_id,
            RepairReport.user_id == user_id,
        )
    )
    return session.execute(stmt).one_or_none()

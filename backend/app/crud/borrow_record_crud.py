from datetime import datetime

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic.alias_generators import to_snake
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.constant.status_constant import BorrowRecordStatus
from app.db.models.borrow_record_model import BorrowRecord
from app.db.models.equipment_category_model import EquipmentCategory
from app.db.models.equipment_model import Equipment
from app.db.models.borrow_return_record_model import BorrowReturnRecord
from app.db.models.user_model import User
from app.schema.admin_borrow_record_schema import AdminBorrowRecordQuery
from app.schema.borrow_record_schema import BorrowRecordQuery


def get_borrow_record_by_equipment_time(
    session: Session,
    equipment_id: int,
    borrow_start_time: datetime,
    borrow_end_time: datetime,
) -> BorrowRecord | None:
    stmt = select(BorrowRecord).where(
        BorrowRecord.equipment_id == equipment_id,
        BorrowRecord.status.in_([
            BorrowRecordStatus.PENDING,
            BorrowRecordStatus.APPROVED,
            BorrowRecordStatus.BORROWED,
            BorrowRecordStatus.PENDING_RETURN,
        ]),
        BorrowRecord.borrow_start_time < borrow_end_time,
        BorrowRecord.borrow_end_time > borrow_start_time,
    )
    return session.scalar(stmt)


def add_borrow_record(borrow_record: BorrowRecord, session: Session) -> None:
    session.add(borrow_record)
    session.flush()


def get_borrow_record_by_id_and_user_for_update(
    session: Session,
    borrow_record_id: int,
    user_id: int,
) -> BorrowRecord | None:
    stmt = (
        select(BorrowRecord)
        .where(
            BorrowRecord.id == borrow_record_id,
            BorrowRecord.user_id == user_id,
        )
        .with_for_update()
    )
    return session.scalar(stmt)


def get_borrow_record_by_id_for_update(
    session: Session,
    borrow_record_id: int,
) -> BorrowRecord | None:
    stmt = select(BorrowRecord).where(BorrowRecord.id == borrow_record_id).with_for_update()
    return session.scalar(stmt)


def update_borrow_record(borrow_record: BorrowRecord, values: dict, session: Session) -> None:
    for field, value in values.items():
        setattr(borrow_record, field, value)
    session.flush()


def get_borrow_record_detail_by_id_and_user(
    session: Session,
    borrow_record_id: int,
    user_id: int,
) -> tuple[BorrowRecord, Equipment | None, EquipmentCategory | None] | None:
    stmt = (
        select(BorrowRecord, Equipment, EquipmentCategory)
        .outerjoin(Equipment, BorrowRecord.equipment_id == Equipment.id)
        .outerjoin(EquipmentCategory, Equipment.category_id == EquipmentCategory.id)
        .where(
            BorrowRecord.id == borrow_record_id,
            BorrowRecord.user_id == user_id,
        )
    )
    return session.execute(stmt).one_or_none()


def query_borrow_record_by_user(
    session: Session,
    user_id: int,
    query: BorrowRecordQuery,
) -> Page[tuple[BorrowRecord, Equipment | None]]:
    stmt = (
        select(BorrowRecord, Equipment)
        .outerjoin(Equipment, BorrowRecord.equipment_id == Equipment.id)
        .where(BorrowRecord.user_id == user_id)
    )
    if query.status:
        stmt = stmt.where(BorrowRecord.status == query.status)
    if query.equipment_name:
        stmt = stmt.where(Equipment.equipment_name.like(f"%{query.equipment_name}%"))
    if query.start_time and query.end_time:
        stmt = stmt.where(BorrowRecord.borrow_start_time.between(query.start_time, query.end_time))
    if query.sort or query.order:
        sort_column = getattr(BorrowRecord, to_snake(query.sort or "id"))
        stmt = stmt.order_by(desc(sort_column) if query.order == "desc" else asc(sort_column))
    return paginate(session, stmt, query)


def query_borrow_record_by_admin(
    session: Session,
    query: AdminBorrowRecordQuery,
) -> Page[tuple[BorrowRecord, User | None, Equipment | None, BorrowReturnRecord | None]]:
    stmt = (
        select(BorrowRecord, User, Equipment, BorrowReturnRecord)
        .outerjoin(User, BorrowRecord.user_id == User.id)
        .outerjoin(Equipment, BorrowRecord.equipment_id == Equipment.id)
        .outerjoin(BorrowReturnRecord, BorrowRecord.id == BorrowReturnRecord.borrow_record_id)
    )
    if query.user_id:
        stmt = stmt.where(BorrowRecord.user_id == query.user_id)
    if query.equipment_id:
        stmt = stmt.where(BorrowRecord.equipment_id == query.equipment_id)
    if query.status:
        stmt = stmt.where(BorrowRecord.status == query.status)
    if query.keyword:
        keyword = f"%{query.keyword}%"
        stmt = stmt.where(
            User.name.like(keyword)
            | User.username.like(keyword)
            | Equipment.equipment_name.like(keyword)
            | Equipment.equipment_no.like(keyword)
        )
    if query.start_time:
        stmt = stmt.where(BorrowRecord.borrow_start_time >= query.start_time)
    if query.end_time:
        stmt = stmt.where(BorrowRecord.borrow_end_time <= query.end_time)
    if query.sort or query.order:
        sort_column = getattr(BorrowRecord, to_snake(query.sort or "id"), BorrowRecord.id)
        stmt = stmt.order_by(desc(sort_column) if query.order == "desc" else asc(sort_column))
    return paginate(session, stmt, query)


def get_borrow_record_detail_by_id_for_admin(
    session: Session,
    borrow_record_id: int,
):
    from app.db.models.repair_order_model import RepairOrder
    from app.db.models.repair_report_model import RepairReport

    stmt = (
        select(
            BorrowRecord,
            User,
            Equipment,
            EquipmentCategory,
            BorrowReturnRecord,
            RepairReport,
            RepairOrder,
        )
        .outerjoin(User, BorrowRecord.user_id == User.id)
        .outerjoin(Equipment, BorrowRecord.equipment_id == Equipment.id)
        .outerjoin(EquipmentCategory, Equipment.category_id == EquipmentCategory.id)
        .outerjoin(BorrowReturnRecord, BorrowRecord.id == BorrowReturnRecord.borrow_record_id)
        .outerjoin(RepairReport, BorrowReturnRecord.id == RepairReport.return_record_id)
        .outerjoin(RepairOrder, RepairReport.id == RepairOrder.repair_report_id)
        .where(BorrowRecord.id == borrow_record_id)
    )
    return session.execute(stmt).one_or_none()

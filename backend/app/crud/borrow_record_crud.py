from datetime import datetime

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic.alias_generators import to_snake
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.constant.status_constant import BorrowRecordStatus
from app.db.models.borrow_record_model import BorrowRecord
from app.db.models.equipment_model import Equipment
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

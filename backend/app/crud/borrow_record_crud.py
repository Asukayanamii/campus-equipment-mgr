from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constant.status_constant import BorrowRecordStatus
from app.db.models.borrow_record_model import BorrowRecord


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

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.borrow_return_record_model import BorrowReturnRecord


def get_borrow_return_record_by_borrow_record_id(
    session: Session,
    borrow_record_id: int,
) -> BorrowReturnRecord | None:
    stmt = select(BorrowReturnRecord).where(BorrowReturnRecord.borrow_record_id == borrow_record_id)
    return session.scalar(stmt)


def get_borrow_return_record_by_borrow_record_id_for_update(
    session: Session,
    borrow_record_id: int,
) -> BorrowReturnRecord | None:
    stmt = (
        select(BorrowReturnRecord)
        .where(BorrowReturnRecord.borrow_record_id == borrow_record_id)
        .with_for_update()
    )
    return session.scalar(stmt)


def add_borrow_return_record(borrow_return_record: BorrowReturnRecord, session: Session) -> None:
    session.add(borrow_return_record)
    session.flush()


def update_borrow_return_record(borrow_return_record: BorrowReturnRecord, values: dict, session: Session) -> None:
    for field, value in values.items():
        setattr(borrow_return_record, field, value)
    session.flush()

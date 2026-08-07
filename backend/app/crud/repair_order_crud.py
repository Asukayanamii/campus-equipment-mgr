from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.repair_order_model import RepairOrder


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

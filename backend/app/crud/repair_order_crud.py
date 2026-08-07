from sqlalchemy.orm import Session

from app.db.models.repair_order_model import RepairOrder


def add_repair_order(repair_order: RepairOrder, session: Session) -> None:
    session.add(repair_order)
    session.flush()

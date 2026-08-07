from sqlalchemy.orm import Session

from app.db.models.repair_report_model import RepairReport


def add_repair_report(repair_report: RepairReport, session: Session) -> None:
    session.add(repair_report)
    session.flush()

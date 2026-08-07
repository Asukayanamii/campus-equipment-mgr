from sqlalchemy.orm import Session

from app.db.models.audit_record_model import AuditRecord


def add_audit_record(audit_record: AuditRecord, session: Session) -> None:
    session.add(audit_record)
    session.flush()

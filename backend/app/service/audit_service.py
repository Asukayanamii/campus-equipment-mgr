from sqlalchemy.orm import Session

from app.crud import audit_record_crud
from app.db.models.audit_record_model import AuditRecord


def create_audit_record_service(
    session: Session,
    business_type: str,
    business_id: int,
    operation_type: str,
    admin_id: int,
    result: str,
    remark: str | None,
) -> None:
    """在调用方的事务中写入管理员审核操作记录。"""
    audit_record_crud.add_audit_record(
        AuditRecord(
            business_type=business_type,
            business_id=business_id,
            operation_type=operation_type,
            admin_id=admin_id,
            result=result,
            remark=remark,
        ),
        session,
    )

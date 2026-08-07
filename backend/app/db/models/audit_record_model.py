from datetime import datetime

from sqlalchemy import BIGINT, DATETIME, TEXT, VARCHAR, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AuditRecord(Base):
    __tablename__ = "audit_record"
    __table_args__ = (
        Index("idx_audit_record_business", "business_type", "business_id"),
        Index("idx_audit_record_admin_id", "admin_id"),
        {"comment": "管理员审核操作记录表"},
    )

    id: Mapped[int] = mapped_column(BIGINT, autoincrement=True, primary_key=True, comment="审核记录主键")
    business_type: Mapped[str] = mapped_column(VARCHAR(30), nullable=False, comment="业务类型")
    business_id: Mapped[int] = mapped_column(BIGINT, nullable=False, comment="业务记录 ID")
    operation_type: Mapped[str] = mapped_column(VARCHAR(30), nullable=False, comment="操作类型")
    admin_id: Mapped[int] = mapped_column(BIGINT, nullable=False, comment="操作管理员 ID")
    result: Mapped[str] = mapped_column(VARCHAR(30), nullable=False, comment="审核结果")
    remark: Mapped[str | None] = mapped_column(TEXT, nullable=True, comment="审核备注")
    create_time: Mapped[datetime] = mapped_column(DATETIME, default=datetime.now, nullable=False, comment="创建时间")

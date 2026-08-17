from datetime import datetime

from sqlalchemy import BIGINT, DATETIME, TEXT, VARCHAR, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class OperationLog(Base):
    """统一记录审核动作和业务状态变更历史。"""

    __tablename__ = "operation_log"
    __table_args__ = (
        Index("idx_operation_log_business", "business_type", "business_id", "create_time"),
        Index("idx_operation_log_equipment", "equipment_id", "create_time"),
        {"comment": "业务操作与状态变更日志表"},
    )

    id: Mapped[int] = mapped_column(BIGINT, autoincrement=True, primary_key=True, comment="日志主键")
    business_type: Mapped[str] = mapped_column(VARCHAR(30), nullable=False, comment="业务类型")
    business_id: Mapped[int] = mapped_column(BIGINT, nullable=False, comment="业务记录 ID")
    equipment_id: Mapped[int | None] = mapped_column(BIGINT, nullable=True, comment="关联设备 ID")
    action: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, comment="操作动作")
    from_status: Mapped[str | None] = mapped_column(VARCHAR(30), nullable=True, comment="变更前状态")
    to_status: Mapped[str | None] = mapped_column(VARCHAR(30), nullable=True, comment="变更后状态")
    operator_role: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, comment="操作者角色")
    operator_id: Mapped[int | None] = mapped_column(BIGINT, nullable=True, comment="操作者 ID")
    remark: Mapped[str | None] = mapped_column(TEXT, nullable=True, comment="操作备注")
    create_time: Mapped[datetime] = mapped_column(DATETIME, default=datetime.now, nullable=False, comment="操作时间")

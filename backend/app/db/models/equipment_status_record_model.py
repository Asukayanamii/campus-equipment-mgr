from datetime import datetime

from sqlalchemy import BIGINT, DATETIME, TEXT, VARCHAR, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class EquipmentStatusRecord(Base):
    __tablename__ = "equipment_status_record"
    __table_args__ = (
        Index("idx_equipment_status_record_equipment_id", "equipment_id"),
        Index("idx_equipment_status_record_business", "business_type", "business_id"),
        {"comment": "设备状态变更记录表"},
    )

    id: Mapped[int] = mapped_column(BIGINT, autoincrement=True, primary_key=True, comment="状态记录主键")
    equipment_id: Mapped[int] = mapped_column(BIGINT, nullable=False, comment="设备 ID")
    before_status: Mapped[str] = mapped_column(VARCHAR(30), nullable=False, comment="变更前设备状态")
    after_status: Mapped[str] = mapped_column(VARCHAR(30), nullable=False, comment="变更后设备状态")
    business_type: Mapped[str] = mapped_column(VARCHAR(30), nullable=False, comment="关联业务类型")
    business_id: Mapped[int] = mapped_column(BIGINT, nullable=False, comment="关联业务记录 ID")
    operator_id: Mapped[int] = mapped_column(BIGINT, nullable=False, comment="操作管理员 ID")
    reason: Mapped[str | None] = mapped_column(TEXT, nullable=True, comment="变更原因")
    create_time: Mapped[datetime] = mapped_column(DATETIME, default=datetime.now, nullable=False, comment="创建时间")

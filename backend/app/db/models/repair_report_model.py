from datetime import datetime

from sqlalchemy import BIGINT, VARCHAR, TEXT, DATETIME, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.constant.status_constant import RepairReportStatus
from app.db.session import Base


class RepairReport(Base):
    __tablename__ = "repair_report"
    __table_args__ = (
        UniqueConstraint("return_record_id", name="uk_repair_report_return_record_id"),
        Index("idx_repair_report_equipment_id", "equipment_id"),
        Index("idx_repair_report_user_id", "user_id"),
        {"comment": "设备报修记录表"}
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        autoincrement=True,
        primary_key=True,
        comment="报修记录主键"
    )

    return_record_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="归还记录 ID"
    )

    user_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="报修用户 ID"
    )

    equipment_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="设备 ID"
    )

    damage_description: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
        comment="损坏说明"
    )

    status: Mapped[str] = mapped_column(
        VARCHAR(30),
        default=RepairReportStatus.PENDING,
        nullable=False,
        comment="报修状态"
    )

    create_time: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.now,
        nullable=False
    )

    update_time: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )

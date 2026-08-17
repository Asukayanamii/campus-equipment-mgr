from datetime import datetime

from sqlalchemy import BIGINT, VARCHAR, TEXT, DATETIME, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.constant.status_constant import BorrowRecordStatus
from app.db.session import Base


class BorrowRecord(Base):
    __tablename__ = "borrow_record"
    __table_args__ = (
        Index("idx_borrow_record_user_id", "user_id"),
        Index("idx_borrow_record_equipment_time", "equipment_id", "borrow_start_time", "borrow_end_time"),
        {"comment": "设备借用记录表"}
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        autoincrement=True,
        primary_key=True,
        comment="借用记录主键"
    )

    user_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="借用用户 ID"
    )

    equipment_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="设备 ID"
    )

    borrow_start_time: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False,
        comment="借用开始时间"
    )

    borrow_end_time: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False,
        comment="借用结束时间"
    )

    purpose: Mapped[str | None] = mapped_column(
        VARCHAR(500),
        nullable=True,
        comment="借用用途"
    )

    status: Mapped[str] = mapped_column(
        VARCHAR(30),
        default=BorrowRecordStatus.PENDING,
        nullable=False,
        comment="借用状态"
    )

    review_remark: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
        comment="审核备注"
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

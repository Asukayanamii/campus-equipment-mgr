from datetime import datetime

from sqlalchemy import BIGINT, VARCHAR, TEXT, DATETIME, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.constant.status_constant import BorrowReturnStatus, ConfirmStatus
from app.db.session import Base


class BorrowReturnRecord(Base):
    __tablename__ = "borrow_return_record"
    __table_args__ = (
        UniqueConstraint("borrow_record_id", name="uk_borrow_return_record_borrow_record_id"),
        {"comment": "设备归还记录表"}
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        autoincrement=True,
        primary_key=True,
        comment="归还记录主键"
    )

    borrow_record_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="借用记录 ID"
    )

    return_status: Mapped[str] = mapped_column(
        VARCHAR(30),
        nullable=False,
        comment="归还状态"
    )

    return_remark: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
        comment="归还说明"
    )

    damage_description: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
        comment="损坏说明"
    )

    return_time: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.now,
        nullable=False,
        comment="提交归还时间"
    )

    confirm_status: Mapped[str] = mapped_column(
        VARCHAR(30),
        default=ConfirmStatus.PENDING,
        nullable=False,
        comment="管理员确认状态"
    )

    confirm_remark: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
        comment="管理员确认备注"
    )

    confirmer_id: Mapped[int | None] = mapped_column(
        BIGINT,
        nullable=True,
        comment="确认管理员 ID"
    )

    confirm_time: Mapped[datetime | None] = mapped_column(
        DATETIME,
        nullable=True,
        comment="确认时间"
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

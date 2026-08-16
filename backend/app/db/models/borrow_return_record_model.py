from datetime import datetime

from sqlalchemy import BIGINT, VARCHAR, TEXT, DATETIME, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

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

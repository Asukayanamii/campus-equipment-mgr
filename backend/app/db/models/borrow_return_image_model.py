from datetime import datetime

from sqlalchemy import BIGINT, VARCHAR, Integer, DATETIME, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class BorrowReturnImage(Base):
    __tablename__ = "borrow_return_image"
    __table_args__ = (
        Index("idx_borrow_return_image_return_record_id", "return_record_id"),
        {"comment": "设备归还图片表"}
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        autoincrement=True,
        primary_key=True,
        comment="归还图片主键"
    )

    return_record_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="归还记录 ID"
    )

    image_url: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=False,
        comment="图片地址"
    )

    sort: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="图片排序"
    )

    create_time: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.now,
        nullable=False
    )

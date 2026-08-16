from datetime import datetime

from sqlalchemy import BIGINT, DATETIME, Integer, VARCHAR, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RepairOrderImage(Base):
    __tablename__ = "repair_order_image"
    __table_args__ = (
        Index("idx_repair_order_image_order_id", "repair_order_id"),
        {"comment": "维修工单凭证图片表"},
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        autoincrement=True,
        primary_key=True,
        comment="维修图片主键",
    )

    repair_order_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="维修工单 ID",
    )

    image_type: Mapped[str] = mapped_column(
        VARCHAR(20),
        nullable=False,
        comment="图片类型：before/after",
    )

    image_url: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=False,
        comment="图片地址",
    )

    sort: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="同类型图片排序",
    )

    create_time: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.now,
        nullable=False,
    )

from datetime import datetime
from sqlalchemy import BIGINT, VARCHAR, Integer, DATETIME, UniqueConstraint
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.session import Base


class EquipmentCategory(Base):
    __tablename__ = "equipment_category"
    __table_args__ = (
        UniqueConstraint("category_name", name="uk_category_name"),
        {"comment": "设备分类表"}
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        autoincrement=True,
        primary_key=True,
        comment="分类ID"
    )

    category_name: Mapped[str] = mapped_column(
        VARCHAR(50),
        nullable=False,
        comment="分类名称"
    )

    sort: Mapped[int | None] = mapped_column(
        Integer,
        default=0,
        nullable=True,
        comment="排序"
    )

    is_deleted: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        nullable=False
    )

    create_time: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False,
        default=datetime.now
    )

    update_time: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now
    )
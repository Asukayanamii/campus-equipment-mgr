from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import BIGINT, VARCHAR, DATE, DECIMAL, TEXT, DATETIME, UniqueConstraint
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.session import Base


class Equipment(Base):
    __tablename__ = "equipment"
    __table_args__ = (
        UniqueConstraint("equipment_no", name="uk_equipment_no"),
        {"comment": "设备实物主表"}
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        autoincrement=True,
        primary_key=True,
        comment="设备主键"
    )

    equipment_no: Mapped[str] = mapped_column(
        VARCHAR(60),
        nullable=False,
        comment="资产编号，全局唯一"
    )

    equipment_name: Mapped[str] = mapped_column(
        VARCHAR(100),
        nullable=False,
        comment="设备名称"
    )

    category_id: Mapped[int | None] = mapped_column(
        BIGINT,
        nullable=True,
        comment="所属分类ID"
    )

    spec: Mapped[str | None] = mapped_column(
        VARCHAR(200),
        default="",
        nullable=True,
        comment="规格型号"
    )

    brand: Mapped[str | None] = mapped_column(
        VARCHAR(80),
        default="",
        nullable=True,
        comment="品牌"
    )

    unit: Mapped[str | None] = mapped_column(
        VARCHAR(20),
        default="台",
        nullable=True,
        comment="单位"
    )

    location: Mapped[str | None] = mapped_column(
        VARCHAR(100),
        default="",
        nullable=True,
        comment="存放位置"
    )

    purchase_date: Mapped[date | None] = mapped_column(
        DATE,
        nullable=True,
        comment="采购日期"
    )

    price: Mapped[Decimal | None] = mapped_column(
        DECIMAL(10, 2),
        default=Decimal("0.00"),
        nullable=True,
        comment="采购单价"
    )

    cover_img: Mapped[str | None] = mapped_column(
        VARCHAR(255),
        default="",
        nullable=True,
        comment="设备封面图地址"
    )

    status: Mapped[str] = mapped_column(
        VARCHAR(30),
        default="available",
        nullable=False,
        comment="设备状态枚举"
    )

    remark: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
        comment="备注"
    )

    # 修复TINYINT导入问题
    is_deleted: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        nullable=False,
        comment="0正常 1下架删除"
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
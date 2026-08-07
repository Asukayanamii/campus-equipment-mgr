from datetime import datetime

from sqlalchemy import BIGINT, VARCHAR, TEXT, DATETIME, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.constant.status_constant import RepairOrderStatus
from app.db.session import Base


class RepairOrder(Base):
    __tablename__ = "repair_order"
    __table_args__ = (
        UniqueConstraint("repair_report_id", name="uk_repair_order_repair_report_id"),
        Index("idx_repair_order_equipment_id", "equipment_id"),
        Index("idx_repair_order_repair_user_id", "repair_user_id"),
        {"comment": "设备维修工单表"}
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        autoincrement=True,
        primary_key=True,
        comment="维修工单主键"
    )

    repair_report_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="报修记录 ID"
    )

    equipment_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="设备 ID"
    )

    repair_user_id: Mapped[int | None] = mapped_column(
        BIGINT,
        nullable=True,
        comment="维修人员 ID"
    )

    status: Mapped[str] = mapped_column(
        VARCHAR(30),
        default=RepairOrderStatus.PENDING_ASSIGN,
        nullable=False,
        comment="维修工单状态"
    )

    assign_remark: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
        comment="派单备注"
    )

    assign_time: Mapped[datetime | None] = mapped_column(
        DATETIME,
        nullable=True,
        comment="派单时间"
    )

    fault_cause: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
        comment="故障原因"
    )

    repair_process: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
        comment="维修过程"
    )

    repair_result: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
        comment="维修结果"
    )

    completion_time: Mapped[datetime | None] = mapped_column(
        DATETIME,
        nullable=True,
        comment="提交维修完成时间"
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

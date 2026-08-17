from datetime import datetime
from sqlalchemy import BIGINT, VARCHAR, DATETIME, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.session import Base


class RepairUser(Base):
    __tablename__ = "repair_user"
    __table_args__ = (
        UniqueConstraint("username", name="username"),
        {"comment": "维修员表"}
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        autoincrement=True,
        primary_key=True,
        comment="维修员id"
    )

    name: Mapped[str | None] = mapped_column(
        VARCHAR(32),
        nullable=True,
        comment="姓名"
    )

    username: Mapped[str] = mapped_column(
        VARCHAR(32),
        nullable=False,
        comment="用户名"
    )

    password: Mapped[str | None] = mapped_column(
        VARCHAR(64),
        nullable=True,
        comment="密码"
    )

    image: Mapped[str | None] = mapped_column(
        VARCHAR(255),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        VARCHAR(64),
        nullable=True,
        comment="邮箱"
    )

    create_time: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False,
        default=datetime.now,
        comment="创建时间"
    )

    update_time: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )
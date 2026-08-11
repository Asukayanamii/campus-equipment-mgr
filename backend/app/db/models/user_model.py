from datetime import datetime
from sqlalchemy import BIGINT, VARCHAR, DATETIME, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.session import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("username", name="username"),
        UniqueConstraint("email", name="uq_user_email"),
        {"comment": "用户表"}
    )

    # 用户主键
    id: Mapped[int] = mapped_column(
        BIGINT,
        autoincrement=True,
        primary_key=True,
        comment="用户id"
    )

    # 姓名 可空
    name: Mapped[str | None] = mapped_column(
        VARCHAR(32),
        nullable=True,
        comment="姓名"
    )

    # 用户名 唯一非空
    username: Mapped[str] = mapped_column(
        VARCHAR(32),
        nullable=False,
        comment="用户名"
    )

    # 密码 可空
    password: Mapped[str | None] = mapped_column(
        VARCHAR(64),
        nullable=True,
        comment="密码"
    )

    # 头像地址
    image: Mapped[str | None] = mapped_column(
        VARCHAR(255),
        nullable=True
    )

    # 邮箱
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

from datetime import datetime

from sqlalchemy import BIGINT, BOOLEAN, DATETIME, VARCHAR, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RegistrationCode(Base):
    __tablename__ = "registration_code"
    __table_args__ = (
        UniqueConstraint("code", name="registration_code_code"),
        {"comment": "管理员与维修员注册码表"},
    )

    id: Mapped[int] = mapped_column(BIGINT, autoincrement=True, primary_key=True, comment="注册码 ID")
    code: Mapped[str] = mapped_column(VARCHAR(128), nullable=False, comment="plain registration code")
    code_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, comment="注册码适用账号类型")
    is_used: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False, comment="whether used")
    create_time: Mapped[datetime] = mapped_column(DATETIME, nullable=False, default=datetime.now, comment="create time")
    update_time: Mapped[datetime] = mapped_column(
        DATETIME, nullable=False, default=datetime.now, onupdate=datetime.now, comment="update time"
    )

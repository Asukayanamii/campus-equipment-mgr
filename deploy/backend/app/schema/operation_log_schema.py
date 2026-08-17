from datetime import datetime

from pydantic import Field, field_serializer, field_validator

from app.constant.status_constant import (
    OPERATION_ACTION_CODES,
    OPERATION_ACTION_MAP,
    OPERATION_ACTOR_ROLE_CODES,
    OPERATION_ACTOR_ROLE_MAP,
    OPERATION_BUSINESS_TYPE_CODES,
    OPERATION_BUSINESS_TYPE_MAP,
)
from app.schema.base_schema import BaseSchema
from app.schema.common_schema import PageQuery


class OperationLogQuery(PageQuery):
    """管理员分页查询操作日志的条件。"""

    business_type: str | None = Field(None, description="业务类型")
    business_id: int | None = Field(None, ge=1, description="业务记录 ID")
    equipment_id: int | None = Field(None, ge=1, description="设备 ID")
    action: str | None = Field(None, description="操作动作")
    operator_role: str | None = Field(None, description="操作者角色")
    operator_id: int | None = Field(None, ge=1, description="操作者 ID")

    @field_validator("business_type")
    def validate_business_type(cls, value: str | None):
        if value is not None and value not in OPERATION_BUSINESS_TYPE_CODES:
            raise ValueError("业务类型不合法")
        return value

    @field_validator("action")
    def validate_action(cls, value: str | None):
        if value is not None and value not in OPERATION_ACTION_CODES:
            raise ValueError("操作动作不合法")
        return value

    @field_validator("operator_role")
    def validate_operator_role(cls, value: str | None):
        if value is not None and value not in OPERATION_ACTOR_ROLE_CODES:
            raise ValueError("操作者角色不合法")
        return value


class OperationLogOut(BaseSchema):
    """业务操作日志响应模型。"""

    id: int = Field(..., description="日志 ID")
    business_type: str = Field(..., description="业务类型")
    business_id: int = Field(..., description="业务记录 ID")
    equipment_id: int | None = Field(None, description="关联设备 ID")
    action: str = Field(..., description="操作动作")
    from_status: str | None = Field(None, description="变更前状态")
    to_status: str | None = Field(None, description="变更后状态")
    operator_role: str = Field(..., description="操作者角色")
    operator_id: int | None = Field(None, description="操作者 ID")
    remark: str | None = Field(None, description="操作备注")
    create_time: datetime = Field(..., description="操作时间")

    @field_serializer("business_type")
    def serialize_business_type(self, value: str):
        return OPERATION_BUSINESS_TYPE_MAP.get(value, value)

    @field_serializer("action")
    def serialize_action(self, value: str):
        return OPERATION_ACTION_MAP.get(value, value)

    @field_serializer("operator_role")
    def serialize_operator_role(self, value: str):
        return OPERATION_ACTOR_ROLE_MAP.get(value, value)

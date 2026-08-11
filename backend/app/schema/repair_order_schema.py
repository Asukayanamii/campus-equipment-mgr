from datetime import datetime

from fastapi_pagination import Params
from pydantic import Field, field_serializer, field_validator

from app.constant.status_constant import (
    ITEM_STATUS_MAP,
    REPAIR_ORDER_STATUS_CODES,
    REPAIR_ORDER_STATUS_MAP,
)
from app.schema.base_schema import BaseSchema


class RepairOrderStatusOut(BaseSchema):
    status: str = Field(..., description="维修工单状态")

    @field_serializer("status")
    def serialize_status(self, value: str):
        return REPAIR_ORDER_STATUS_MAP.get(value, value)


class RepairOrderQuery(BaseSchema, Params):
    page: int | None = Field(1, ge=1, le=10000, description="页码")
    size: int | None = Field(10, ge=1, le=100, description="每页条数")
    status: str | None = Field(None, description="维修工单状态编码")
    equipment_name: str | None = Field(None, max_length=100, description="设备名称")
    repair_user_id: int | None = Field(None, ge=1, description="维修人员 ID")

    @field_validator("status")
    def validate_status(cls, value: str | None):
        if value is not None and value not in REPAIR_ORDER_STATUS_CODES:
            raise ValueError("维修工单状态不合法")
        return value


class RepairOrderPageOut(RepairOrderStatusOut):
    id: int = Field(..., description="维修工单 ID")
    repair_report_id: int = Field(..., description="报修记录 ID")
    equipment_id: int = Field(..., description="设备 ID")
    equipment_name: str | None = Field(None, description="设备名称")
    repair_user_id: int | None = Field(None, description="维修人员 ID")
    repair_user_name: str | None = Field(None, description="维修人员姓名")
    assign_time: datetime | None = Field(None, description="派单时间")
    completion_time: datetime | None = Field(None, description="提交维修完成时间")
    create_time: datetime = Field(..., description="创建时间")


class RepairOrderOut(RepairOrderStatusOut):
    id: int = Field(..., description="维修工单 ID")
    repair_report_id: int = Field(..., description="报修记录 ID")
    equipment_id: int = Field(..., description="设备 ID")
    equipment_no: str | None = Field(None, description="设备编号")
    equipment_name: str | None = Field(None, description="设备名称")
    equipment_status: str | None = Field(None, description="设备状态")
    user_id: int | None = Field(None, description="报修用户 ID")
    user_name: str | None = Field(None, description="报修用户姓名")
    damage_description: str | None = Field(None, description="损坏说明")
    damage_images: list[str] = Field(default_factory=list, description="损坏图片地址")
    repair_user_id: int | None = Field(None, description="维修人员 ID")
    repair_user_name: str | None = Field(None, description="维修人员姓名")
    assign_remark: str | None = Field(None, description="派单备注")
    assign_time: datetime | None = Field(None, description="派单时间")
    fault_cause: str | None = Field(None, description="故障原因")
    repair_process: str | None = Field(None, description="维修过程")
    repair_result: str | None = Field(None, description="维修结果")
    before_images: list[str] = Field(default_factory=list, description="维修前图片地址")
    after_images: list[str] = Field(default_factory=list, description="维修后图片地址")
    completion_time: datetime | None = Field(None, description="提交维修完成时间")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("equipment_status")
    def serialize_equipment_status(self, value: str | None):
        return ITEM_STATUS_MAP.get(value, value) if value else None


class RepairOrderActionOut(RepairOrderStatusOut):
    id: int = Field(..., description="维修工单 ID")
    equipment_id: int = Field(..., description="设备 ID")
    equipment_status: str | None = Field(None, description="设备状态")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("equipment_status")
    def serialize_equipment_status(self, value: str | None):
        return ITEM_STATUS_MAP.get(value, value) if value else None


class RepairOrderAssignIn(BaseSchema):
    repair_user_id: int = Field(..., ge=1, description="维修人员 ID")
    assign_remark: str | None = Field(None, max_length=1000, description="派单备注")


class RepairOrderAssignOut(RepairOrderActionOut):
    repair_report_id: int = Field(..., description="报修记录 ID")
    repair_user_id: int = Field(..., description="维修人员 ID")
    assign_remark: str | None = Field(None, description="派单备注")
    assign_time: datetime = Field(..., description="派单时间")


class RepairOrderCompletionIn(BaseSchema):
    result_status: str = Field(..., pattern="^(repaired|unrepairable)$", description="维修结果状态")
    fault_cause: str = Field(..., min_length=1, max_length=2000, description="故障原因")
    repair_process: str = Field(..., min_length=1, max_length=4000, description="维修过程")
    repair_result: str = Field(..., min_length=1, max_length=2000, description="维修结果")
    before_images: list[str] = Field(..., min_length=1, max_length=9, description="维修前图片地址")
    after_images: list[str] = Field(..., min_length=1, max_length=9, description="维修后图片地址")

    @field_validator("before_images", "after_images")
    def validate_images(cls, value: list[str]):
        if any(not image.strip() for image in value):
            raise ValueError("图片地址不能为空")
        return value


class RepairOrderCompletionOut(RepairOrderActionOut):
    fault_cause: str = Field(..., description="故障原因")
    repair_process: str = Field(..., description="维修过程")
    repair_result: str = Field(..., description="维修结果")
    before_images: list[str] = Field(default_factory=list, description="维修前图片地址")
    after_images: list[str] = Field(default_factory=list, description="维修后图片地址")
    completion_time: datetime = Field(..., description="提交维修完成时间")


class RepairUserPageOut(BaseSchema):
    id: int = Field(..., description="维修人员 ID")
    name: str | None = Field(None, description="维修人员姓名")
    username: str = Field(..., description="维修人员账号")


class RepairReportAdminPageOut(BaseSchema):
    id: int = Field(..., description="报修记录 ID")
    user_id: int = Field(..., description="报修用户 ID")
    user_name: str | None = Field(None, description="报修用户姓名")
    equipment_id: int = Field(..., description="设备 ID")
    equipment_name: str | None = Field(None, description="设备名称")
    status: str = Field(..., description="报修状态")
    repair_order_id: int | None = Field(None, description="维修工单 ID")
    repair_order_status: str | None = Field(None, description="维修工单状态")
    create_time: datetime = Field(..., description="创建时间")

    @field_serializer("status")
    def serialize_report_status(self, value: str):
        from app.constant.status_constant import REPAIR_REPORT_STATUS_MAP
        return REPAIR_REPORT_STATUS_MAP.get(value, value)

    @field_serializer("repair_order_status")
    def serialize_order_status(self, value: str | None):
        return REPAIR_ORDER_STATUS_MAP.get(value, value) if value else None


class RepairReportAdminOut(BaseSchema):
    id: int = Field(..., description="报修记录 ID")
    return_record_id: int = Field(..., description="归还记录 ID")
    user_id: int = Field(..., description="报修用户 ID")
    user_name: str | None = Field(None, description="报修用户姓名")
    username: str | None = Field(None, description="报修用户账号")
    equipment_id: int = Field(..., description="设备 ID")
    equipment_no: str | None = Field(None, description="设备编号")
    equipment_name: str | None = Field(None, description="设备名称")
    damage_description: str = Field(..., description="损坏说明")
    damage_images: list[str] = Field(default_factory=list, description="损坏图片地址")
    status: str = Field(..., description="报修状态")
    repair_order_id: int | None = Field(None, description="维修工单 ID")
    repair_order_status: str | None = Field(None, description="维修工单状态")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("status")
    def serialize_report_status(self, value: str):
        from app.constant.status_constant import REPAIR_REPORT_STATUS_MAP
        return REPAIR_REPORT_STATUS_MAP.get(value, value)

    @field_serializer("repair_order_status")
    def serialize_order_status(self, value: str | None):
        return REPAIR_ORDER_STATUS_MAP.get(value, value) if value else None


class RepairReportConfirmOut(BaseSchema):
    id: int = Field(..., description="报修记录 ID")
    status: str = Field(..., description="报修状态")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("status")
    def serialize_status(self, value: str):
        from app.constant.status_constant import REPAIR_REPORT_STATUS_MAP
        return REPAIR_REPORT_STATUS_MAP.get(value, value)

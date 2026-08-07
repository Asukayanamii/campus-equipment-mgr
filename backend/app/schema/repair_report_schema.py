from datetime import date, datetime
from decimal import Decimal

from fastapi_pagination import Params
from pydantic import field_serializer, Field, field_validator

from app.constant.status_constant import CONFIRM_STATUS_MAP, ITEM_STATUS_MAP, REPAIR_ORDER_STATUS_MAP, REPAIR_REPORT_STATUS_CODES, REPAIR_REPORT_STATUS_MAP
from app.schema.base_schema import BaseSchema


class RepairReportStatusOut(BaseSchema):
    """报修记录状态响应模型"""
    status: str = Field(..., description="报修状态")

    @field_serializer("status")
    def serialize_status(self, value: str):
        return REPAIR_REPORT_STATUS_MAP.get(value, value)


class RepairReportPageOut(RepairReportStatusOut):
    """报修记录分页响应模型"""
    id: int = Field(..., description="报修记录 ID")
    equipment_id: int = Field(..., description="设备 ID")
    equipment_name: str | None = Field(None, description="设备名称")
    create_time: datetime = Field(..., description="创建时间")


class RepairReportOut(RepairReportStatusOut):
    """报修记录详情响应模型"""
    id: int = Field(..., description="报修记录 ID")
    return_record_id: int = Field(..., description="归还记录 ID")
    user_id: int = Field(..., description="报修用户 ID")
    equipment_id: int = Field(..., description="设备 ID")
    equipment_no: str | None = Field(None, description="设备编号")
    equipment_name: str | None = Field(None, description="设备名称")
    category_id: int | None = Field(None, description="设备分类 ID")
    category_name: str | None = Field(None, description="设备分类名称")
    spec: str | None = Field(None, description="设备规格型号")
    brand: str | None = Field(None, description="设备品牌")
    unit: str | None = Field(None, description="设备计量单位")
    location: str | None = Field(None, description="设备存放位置")
    purchase_date: date | None = Field(None, description="设备采购日期")
    price: Decimal | None = Field(None, description="设备采购价格")
    cover_img: str | None = Field(None, description="设备封面图片")
    equipment_status: str | None = Field(None, description="设备状态")
    remark: str | None = Field(None, description="设备备注")
    damage_description: str = Field(..., description="损坏说明")
    damage_images: list[str] = Field(default_factory=list, description="损坏图片地址")
    confirm_status: str = Field(..., description="管理员确认状态")
    confirm_remark: str | None = Field(None, description="管理员确认备注")
    confirmer_id: int | None = Field(None, description="确认管理员 ID")
    confirm_time: datetime | None = Field(None, description="确认时间")
    repair_order_id: int | None = Field(None, description="维修工单 ID")
    repair_user_id: int | None = Field(None, description="维修人员 ID")
    repair_status: str | None = Field(None, description="维修工单状态")
    assign_remark: str | None = Field(None, description="派单备注")
    assign_time: datetime | None = Field(None, description="派单时间")
    fault_cause: str | None = Field(None, description="故障原因")
    repair_process: str | None = Field(None, description="维修过程")
    repair_result: str | None = Field(None, description="维修结果")
    completion_time: datetime | None = Field(None, description="提交维修完成时间")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("price")
    def serialize_price(self, value: Decimal | None):
        if value is None:
            return None
        return str(value)

    @field_serializer("purchase_date")
    def serialize_date(self, value: date | None):
        return value.strftime("%Y-%m-%d") if value else None

    @field_serializer("equipment_status")
    def serialize_equipment_status(self, value: str | None):
        if value is None:
            return None
        return ITEM_STATUS_MAP.get(value, value)

    @field_serializer("confirm_status")
    def serialize_confirm_status(self, value: str):
        return CONFIRM_STATUS_MAP.get(value, value)

    @field_serializer("repair_status")
    def serialize_repair_status(self, value: str | None):
        if value is None:
            return None
        return REPAIR_ORDER_STATUS_MAP.get(value, value)


class RepairReportQuery(BaseSchema, Params):
    """报修记录分页查询参数"""
    page: int | None = Field(1, ge=1, le=10000, description="页码")
    size: int | None = Field(10, ge=1, le=100, description="每页条数")
    status: str | None = Field(None, description="报修状态")
    equipment_name: str | None = Field(None, max_length=100, description="设备名称")
    sort: str | None = Field("id", description="排序字段")
    order: str | None = Field("asc", pattern="^(asc|desc)$", description="排序顺序")

    @field_validator("status")
    def validate_status(cls, value: str | None):
        if value is not None and value not in REPAIR_REPORT_STATUS_CODES:
            raise ValueError("报修状态不合法")
        return value

    @field_validator("*", mode="before")
    def empty_str_to_default_or_none(cls, value, info):
        if isinstance(value, str) and value.strip() == "":
            if info.field_name == "page":
                return 1
            if info.field_name == "size":
                return 10
            return None
        return value

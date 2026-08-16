from datetime import date, datetime
from decimal import Decimal

from fastapi_pagination import Params
from pydantic import Field, field_serializer, field_validator

from app.constant.status_constant import (
    BORROW_RECORD_STATUS_CODES,
    BORROW_RECORD_STATUS_MAP,
    BORROW_RETURN_STATUS_CODES,
    BORROW_RETURN_STATUS_MAP,
    ITEM_STATUS_MAP,
    REPAIR_ORDER_STATUS_MAP,
    REPAIR_REPORT_STATUS_MAP,
)
from app.schema.base_schema import BaseSchema


class AdminBorrowRecordQuery(BaseSchema, Params):
    """管理员借用记录分页查询参数"""
    page: int | None = Field(1, ge=1, le=10000, description="页码")
    size: int | None = Field(10, ge=1, le=100, description="每页条数")
    user_id: int | None = Field(None, ge=1, description="申请人 ID")
    equipment_id: int | None = Field(None, ge=1, description="设备 ID")
    status: str | None = Field(None, description="借用状态")
    keyword: str | None = Field(None, max_length=100, description="申请人或设备关键字")
    start_time: datetime | None = Field(None, description="借用开始时间下限")
    end_time: datetime | None = Field(None, description="借用结束时间上限")
    sort: str | None = Field("id", description="排序字段")
    order: str | None = Field("asc", pattern="^(asc|desc)$", description="排序顺序")

    @field_validator("status")
    def validate_status(cls, value: str | None):
        if value is not None and value not in BORROW_RECORD_STATUS_CODES:
            raise ValueError("借用状态不合法")
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


class AdminBorrowRecordPageOut(BaseSchema):
    """管理员借用记录分页单条响应模型"""
    id: int = Field(..., description="借用记录 ID")
    user_id: int = Field(..., description="申请人 ID")
    user_name: str | None = Field(None, description="申请人姓名")
    username: str | None = Field(None, description="申请人用户名")
    equipment_id: int = Field(..., description="设备 ID")
    equipment_name: str | None = Field(None, description="设备名称")
    borrow_start_time: datetime = Field(..., description="借用开始时间")
    borrow_end_time: datetime = Field(..., description="借用结束时间")
    status: str = Field(..., description="借用状态")
    return_status: str | None = Field(None, description="学生申报归还状态")
    create_time: datetime = Field(..., description="创建时间")

    @field_serializer("status")
    def serialize_status(self, value: str):
        return BORROW_RECORD_STATUS_MAP.get(value, value)
    @field_serializer("return_status")
    def serialize_return_status(self, value: str | None):
        return BORROW_RETURN_STATUS_MAP.get(value, value) if value else None


class AdminBorrowRecordOut(BaseSchema):
    """管理员借用记录详情响应模型"""
    id: int = Field(..., description="借用记录 ID")
    user_id: int = Field(..., description="申请人 ID")
    user_name: str | None = Field(None, description="申请人姓名")
    username: str | None = Field(None, description="申请人用户名")
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
    borrow_start_time: datetime = Field(..., description="借用开始时间")
    borrow_end_time: datetime = Field(..., description="借用结束时间")
    purpose: str | None = Field(None, description="借用用途")
    status: str = Field(..., description="借用状态")
    review_remark: str | None = Field(None, description="审核备注")
    return_record_id: int | None = Field(None, description="归还记录 ID")
    return_status: str | None = Field(None, description="学生申报归还状态")
    return_remark: str | None = Field(None, description="归还说明")
    damage_description: str | None = Field(None, description="损坏说明")
    damage_images: list[str] = Field(default_factory=list, description="损坏图片地址")
    return_time: datetime | None = Field(None, description="提交归还时间")
    repair_report_id: int | None = Field(None, description="报修记录 ID")
    repair_report_status: str | None = Field(None, description="报修状态")
    repair_order_id: int | None = Field(None, description="维修工单 ID")
    repair_order_status: str | None = Field(None, description="维修工单状态")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("price")
    def serialize_price(self, value: Decimal | None):
        return str(value) if value is not None else None

    @field_serializer("purchase_date")
    def serialize_purchase_date(self, value: date | None):
        return value.strftime("%Y-%m-%d") if value else None

    @field_serializer("status")
    def serialize_status(self, value: str):
        return BORROW_RECORD_STATUS_MAP.get(value, value)

    @field_serializer("equipment_status")
    def serialize_equipment_status(self, value: str | None):
        return ITEM_STATUS_MAP.get(value, value) if value else None

    @field_serializer("return_status")
    def serialize_return_status(self, value: str | None):
        return BORROW_RETURN_STATUS_MAP.get(value, value) if value else None

    @field_serializer("repair_report_status")
    def serialize_repair_report_status(self, value: str | None):
        return REPAIR_REPORT_STATUS_MAP.get(value, value) if value else None

    @field_serializer("repair_order_status")
    def serialize_repair_order_status(self, value: str | None):
        return REPAIR_ORDER_STATUS_MAP.get(value, value) if value else None


class BorrowRecordReview(BaseSchema):
    """管理员审核借用申请请求模型"""
    approved: bool = Field(..., description="是否通过审核")
    review_remark: str | None = Field(None, max_length=2000, description="审核备注")


class BorrowRecordReviewOut(BaseSchema):
    """审核借用申请响应模型"""
    id: int = Field(..., description="借用记录 ID")
    status: str = Field(..., description="借用状态")
    review_remark: str | None = Field(None, description="审核备注")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("status")
    def serialize_status(self, value: str):
        return BORROW_RECORD_STATUS_MAP.get(value, value)

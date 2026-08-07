from datetime import date, datetime
from decimal import Decimal

from fastapi_pagination import Params
from pydantic import field_serializer, Field, field_validator, model_validator

from app.constant.status_constant import BORROW_RECORD_STATUS_CODES, BORROW_RECORD_STATUS_MAP, ITEM_STATUS_MAP
from app.schema.base_schema import BaseSchema


class BorrowRecordCreate(BaseSchema):
    """提交借用申请请求模型"""
    equipment_id: int = Field(..., ge=1, description="设备 ID")
    borrow_start_time: datetime = Field(..., description="借用开始时间")
    borrow_end_time: datetime = Field(..., description="借用结束时间")
    purpose: str | None = Field(None, max_length=500, description="借用用途")

    @model_validator(mode="after")
    def validate_borrow_time(self):
        if self.borrow_end_time <= self.borrow_start_time:
            raise ValueError("借用结束时间必须晚于开始时间")
        return self


class BorrowRecordStatusOut(BaseSchema):
    """借用记录状态响应模型"""
    status: str = Field(..., description="借用状态")

    @field_serializer("status")
    def serialize_status(self, value: str):
        return BORROW_RECORD_STATUS_MAP.get(value, value)


class BorrowRecordPageOut(BorrowRecordStatusOut):
    """借用记录分页响应模型"""
    id: int = Field(..., description="借用记录 ID")
    equipment_id: int = Field(..., description="设备 ID")
    equipment_name: str | None = Field(None, description="设备名称")
    borrow_start_time: datetime = Field(..., description="借用开始时间")
    borrow_end_time: datetime = Field(..., description="借用结束时间")
    create_time: datetime = Field(..., description="创建时间")


class BorrowRecordCreateOut(BorrowRecordStatusOut):
    """借用记录新增响应模型"""
    id: int = Field(..., description="借用记录 ID")
    user_id: int = Field(..., description="借用用户 ID")
    equipment_id: int = Field(..., description="设备 ID")
    borrow_start_time: datetime = Field(..., description="借用开始时间")
    borrow_end_time: datetime = Field(..., description="借用结束时间")
    purpose: str | None = Field(None, description="借用用途")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")


class BorrowRecordOut(BorrowRecordStatusOut):
    """借用记录详情响应模型"""
    id: int = Field(..., description="借用记录 ID")
    user_id: int = Field(..., description="借用用户 ID")
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
    review_remark: str | None = Field(None, description="审核备注")
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


class BorrowRecordQuery(BaseSchema, Params):
    """借用记录分页查询参数"""
    page: int | None = Field(1, ge=1, le=10000, description="页码")
    size: int | None = Field(10, ge=1, le=100, description="每页条数")
    status: str | None = Field(None, description="借用状态")
    equipment_name: str | None = Field(None, max_length=100, description="设备名称")
    start_time: datetime | None = Field(None, description="借用开始时间")
    end_time: datetime | None = Field(None, description="借用结束时间")
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

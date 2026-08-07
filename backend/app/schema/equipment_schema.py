from datetime import date, datetime
from decimal import Decimal

from fastapi_pagination import Params
from pydantic import field_serializer, Field, field_validator, model_validator

from app.constant.status_constant import ITEM_STATUS_CODES
from app.schema.base_schema import BaseSchema
from app.schema.common_schema import PageQuery


class EquipmentOut(BaseSchema):
    """设备详情/列表单条响应模型"""
    id: int = Field(..., description="设备 ID")
    equipment_no: str = Field(..., description="设备编号")
    equipment_name: str = Field(..., description="设备名称")
    category_id: int | None = Field(None, description="设备分类 ID")
    category_name: str | None = Field(None, description="设备分类名称")
    spec: str | None = Field(None, description="设备规格型号")
    brand: str | None = Field(None, description="设备品牌")
    unit: str | None = Field(None, description="计量单位")
    location: str | None = Field(None, description="设备存放位置")
    purchase_date: date | None = Field(None, description="采购日期")
    price: Decimal | None = Field(None, description="采购价格")
    cover_img: str | None = Field(None, description="设备封面图片")
    status: str = Field("", description="设备状态")
    remark: str | None = Field(None, description="备注")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
    # 序列化时把Decimal转字符串
    @field_serializer("price")
    def serialize_price(self, v: Decimal | None):
        if v is None:
            return None
        return str(v)
    # date 格式化 yyyy-MM-dd
    @field_serializer("purchase_date")
    def serialize_date(self, v: date | None):
        return v.strftime("%Y-%m-%d") if v else None


class EquipmentCreate(BaseSchema):
    """新增设备请求模型"""
    equipment_no: str = Field(..., min_length=1, max_length=60, description="设备编号")
    equipment_name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    category_id: int | None = Field(None, ge=1, description="设备分类 ID")
    spec: str | None = Field(None, max_length=200, description="设备规格型号")
    brand: str | None = Field(None, max_length=80, description="设备品牌")
    unit: str | None = Field(None, max_length=20, description="计量单位")
    location: str | None = Field(None, max_length=100, description="设备存放位置")
    purchase_date: date | None = Field(None, description="采购日期")
    price: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2, description="采购价格")
    cover_img: str | None = Field(None, max_length=255, description="设备封面图片")
    status: str = Field("available", description="设备状态")
    remark: str | None = Field(None, description="备注")

    @field_validator("status")
    def validate_status(cls, value: str):
        if value not in ITEM_STATUS_CODES:
            raise ValueError("设备状态不合法")
        return value


class EquipmentUpdate(BaseSchema):
    """更新设备请求模型，未传字段保持原值不变"""
    equipment_no: str | None = Field(None, min_length=1, max_length=60, description="设备编号")
    equipment_name: str | None = Field(None, min_length=1, max_length=100, description="设备名称")
    category_id: int | None = Field(None, ge=1, description="设备分类 ID")
    spec: str | None = Field(None, max_length=200, description="设备规格型号")
    brand: str | None = Field(None, max_length=80, description="设备品牌")
    unit: str | None = Field(None, max_length=20, description="计量单位")
    location: str | None = Field(None, max_length=100, description="设备存放位置")
    purchase_date: date | None = Field(None, description="采购日期")
    price: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2, description="采购价格")
    cover_img: str | None = Field(None, max_length=255, description="设备封面图片")
    status: str | None = Field(None, description="设备状态")
    remark: str | None = Field(None, description="备注")

    @field_validator("status")
    def validate_status(cls, value: str | None):
        if value is not None and value not in ITEM_STATUS_CODES:
            raise ValueError("设备状态不合法")
        return value

    @model_validator(mode="after")
    def validate_update_fields(self):
        if not self.model_fields_set:
            raise ValueError("至少传入一个需要更新的字段")
        return self

#继承paginate依赖的参数类
class EquipQuery(BaseSchema,Params):
    """设备列表查询参数"""
    page: int | None = Field(default=1, description="页码",ge=1,le=10000)
    size: int | None  = Field(default=10, description="每页条数",ge=1,le=100)
    category_id: int | None = Field(default=None, description="设备分类ID",ge=1)
    status: str | None = Field(default=None, description="设备状态")
    equipment_name: str | None = Field(default=None, description="设备名称")
    equipment_no: str | None = Field(default=None, description="设备编号")
    location: str | None = Field(default=None, description="设备存放位置")
    brand: str | None = Field(default=None, description="设备品牌")
    spec: str | None = Field(default=None, description="设备规格型号")
    start_time: date | None = Field(default=None, description="设备采购开始时间")
    end_time: date | None = Field(default=None, description="设备采购结束时间")
    sort: str | None = Field(default='id', description="排序字段")
    order: str | None = Field(default='asc', description="排序顺序")

    @field_validator("*", mode="before")
    def empty_str_to_none(cls, v, info):
        field_name = info.field_name
        # 判断是不是空字符串
        if isinstance(v, str) and v.strip() == "":
            # 分页关键字段：空串直接返回默认数字，绝不返回None
            if field_name == "page":
                return 1
            elif field_name == "size":
                return 10
            # 其余字段（category_id等）空串转None，不影响
            return None
        # 非空字符串直接原值返回
        return v
    # 校验并转换字符串 -> date
    @field_validator("start_time", mode="before")
    def parse_start_time(cls, value):
        # 空值直接返回
        if value is None or value == "":
            return None
        # 如果已经是date/datetime对象，直接返回
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        # 字符串格式化解析
        return datetime.strptime(value, "%Y-%m-%d").date()
    @field_validator("end_time", mode="before")
    def parse_end_time(cls, value):
        # 空值直接返回
        if value is None or value == "":
            return None
        # 如果已经是date/datetime对象，直接返回
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        # 字符串格式化解析
        return datetime.strptime(value, "%Y-%m-%d").date()

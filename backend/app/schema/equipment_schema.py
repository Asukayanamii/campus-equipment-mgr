from datetime import date, datetime
from decimal import Decimal

from fastapi_pagination import Params
from pydantic import field_serializer, Field, field_validator

from app.schema.base_schema import BaseSchema
from app.schema.common_schema import PageQuery


class EquipmentOut(BaseSchema):
    """设备详情/列表单条响应模型"""
    id: int
    equipment_no: str
    equipment_name: str
    category_name: str | None = None
    spec: str | None = None
    brand: str | None = None
    unit: str | None = None
    location: str | None = None
    purchase_date: date | None = None
    price: Decimal | None = None
    cover_img: str | None = None
    status: str = ""
    remark: str | None = None
    create_time: datetime
    update_time: datetime
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

class EquipQuery(Params):
    """设备列表查询参数"""
    page: int | None = Field(default=1, description="页码")
    size: int | None  = Field(default=10, description="每页条数")
    category_id: int | None = Field(default=None, description="设备分类ID")
    status: str | None = Field(default=None, description="设备状态")
    equipment_name: str | None = Field(default=None, description="设备名称")
    equipment_no: str | None = Field(default=None, description="设备编号")
    location: str | None = Field(default=None, description="设备存放位置")
    brand: str | None = Field(default=None, description="设备品牌")
    spec: str | None = Field(default=None, description="设备规格型号")
    start_time: str | None = Field(default=None, description="设备采购开始时间")
    end_time: str | None = Field(default=None, description="设备采购结束时间")
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
from datetime import date, datetime
from decimal import Decimal

from pydantic import field_serializer

from app.schema.base_schema import BaseSchema


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
from datetime import date, datetime
from decimal import Decimal

from pydantic import field_serializer

from app.schema.base_schema import BaseSchema


class EquipmentOut(BaseSchema):
    """设备详情/列表单条响应模型"""
    id: int
    equipment_no: str
    equipment_name: str
    category_id: int | None
    spec: str | None
    brand: str | None
    unit: str | None
    location: str | None
    purchase_date: date | None
    price: Decimal | None
    cover_img: str | None
    status: str
    remark: str | None
    is_deleted: int
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
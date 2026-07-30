from datetime import datetime

from pydantic import Field

from app.schema.base_schema import BaseSchema


class CategoryResp(BaseSchema):
    id: int = Field(..., description="设备分类 ID")
    category_name: str = Field(..., description="设备分类名称")
    sort: int | None = Field(None, description="排序值")
    is_deleted: int = Field(..., description="删除标记")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

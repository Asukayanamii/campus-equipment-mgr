from datetime import datetime

from fastapi_pagination import Params
from pydantic import Field, field_validator, model_validator

from app.schema.base_schema import BaseSchema


class CategoryResp(BaseSchema):
    id: int = Field(..., description="设备分类 ID")
    category_name: str = Field(..., description="设备分类名称")
    sort: int | None = Field(None, description="排序值")
    is_deleted: int = Field(..., description="删除标记")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")


class CategoryCreate(BaseSchema):
    """新增设备分类请求模型"""
    category_name: str = Field(..., min_length=1, max_length=50, description="设备分类名称")
    sort: int = Field(0, ge=0, description="排序值")


class CategoryUpdate(BaseSchema):
    """更新设备分类请求模型，未传字段保持原值不变"""
    category_name: str | None = Field(None, min_length=1, max_length=50, description="设备分类名称")
    sort: int | None = Field(None, ge=0, description="排序值")

    @model_validator(mode="after")
    def validate_update_fields(self):
        if not self.model_fields_set:
            raise ValueError("至少传入一个需要更新的字段")
        return self


class CategoryQuery(BaseSchema, Params):
    """设备分类分页查询参数"""
    page: int | None = Field(1, ge=1, le=10000, description="页码")
    size: int | None = Field(10, ge=1, le=100, description="每页条数")
    id: int | None = Field(None, ge=1, description="设备分类 ID")
    category_name: str | None = Field(None, max_length=50, description="设备分类名称")
    sort: str | None = Field("sort", description="排序字段")
    order: str | None = Field("asc", pattern="^(asc|desc)$", description="排序顺序")

    @field_validator("*", mode="before")
    def empty_str_to_default_or_none(cls, value, info):
        if isinstance(value, str) and value.strip() == "":
            if info.field_name == "page":
                return 1
            if info.field_name == "size":
                return 10
            return None
        return value

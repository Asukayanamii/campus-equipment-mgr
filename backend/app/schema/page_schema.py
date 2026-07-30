from typing import TypeVar, Generic

from pydantic import Field

from app.schema.base_schema import BaseSchema

T = TypeVar('T')

class PageResp(BaseSchema,Generic[T]):
    total: int = Field(..., description="记录总数")
    records: list[T] = Field(..., description="当前页记录列表")

from typing import TypeVar, Generic

from app.schema.base_schema import BaseSchema

T = TypeVar('T')

class PageResp(BaseSchema,Generic[T]):
    total: int
    records: list[T]

from pydantic import Field

from app.schema.base_schema import BaseSchema


class PageQuery(BaseSchema):
    page: int = Field(default=1, ge=1, le=1000)
    size: int = Field(default=10, ge=1, le=100)

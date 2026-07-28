from datetime import datetime

from app.schema.base_schema import BaseSchema


class CategoryResp(BaseSchema):
    id: int
    category_name: str
    sort: int | None =  None
    is_deleted: int
    create_time: datetime
    update_time: datetime
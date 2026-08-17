from datetime import datetime

from pydantic import BaseModel, field_serializer
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "from_attributes": True  # 必须开启！
    }
    # datetime 格式化 yyyy-MM-dd HH:mm:ss
    @field_serializer("create_time", "update_time",check_fields=False)
    def serialize_datetime(self, v: datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
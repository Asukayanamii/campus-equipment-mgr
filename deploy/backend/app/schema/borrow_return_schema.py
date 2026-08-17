from datetime import datetime

from pydantic import field_serializer, Field, field_validator, model_validator

from app.constant.status_constant import BORROW_RETURN_STATUS_CODES, BORROW_RETURN_STATUS_MAP, BorrowReturnStatus
from app.schema.base_schema import BaseSchema


class BorrowReturnCreate(BaseSchema):
    """提交归还请求模型"""
    return_status: str = Field(..., description="归还状态")
    return_remark: str | None = Field(None, max_length=1000, description="归还说明")
    damage_description: str | None = Field(None, max_length=2000, description="损坏说明")
    damage_images: list[str] = Field(default_factory=list, max_length=9, description="损坏图片地址")

    @field_validator("return_status")
    def validate_return_status(cls, value: str):
        if value not in BORROW_RETURN_STATUS_CODES:
            raise ValueError("归还状态不合法")
        return value

    @field_validator("damage_images")
    def validate_damage_images(cls, value: list[str]):
        if any(not image.strip() for image in value):
            raise ValueError("损坏图片地址不能为空")
        return value

    @model_validator(mode="after")
    def validate_damage_info(self):
        if self.return_status == BorrowReturnStatus.DAMAGED:
            if not self.damage_description or not self.damage_description.strip():
                raise ValueError("设备损坏时必须填写损坏说明")
            if not self.damage_images:
                raise ValueError("设备损坏时必须上传损坏图片")
        elif self.damage_description or self.damage_images:
            raise ValueError("正常归还不能填写损坏信息")
        return self


class BorrowReturnCreateOut(BaseSchema):
    """归还记录新增响应模型"""
    id: int = Field(..., description="归还记录 ID")
    borrow_record_id: int = Field(..., description="借用记录 ID")
    return_status: str = Field(..., description="归还状态")
    return_remark: str | None = Field(None, description="归还说明")
    damage_description: str | None = Field(None, description="损坏说明")
    damage_images: list[str] = Field(default_factory=list, description="损坏图片地址")
    return_time: datetime = Field(..., description="提交归还时间")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("return_status")
    def serialize_return_status(self, value: str):
        return BORROW_RETURN_STATUS_MAP.get(value, value)

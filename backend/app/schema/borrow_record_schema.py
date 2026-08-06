from datetime import datetime

from pydantic import Field, model_validator

from app.schema.base_schema import BaseSchema


class BorrowRecordCreate(BaseSchema):
    """提交借用申请请求模型"""
    equipment_id: int = Field(..., ge=1, description="设备 ID")
    borrow_start_time: datetime = Field(..., description="借用开始时间")
    borrow_end_time: datetime = Field(..., description="借用结束时间")
    purpose: str | None = Field(None, max_length=500, description="借用用途")

    @model_validator(mode="after")
    def validate_borrow_time(self):
        if self.borrow_end_time <= self.borrow_start_time:
            raise ValueError("借用结束时间必须晚于开始时间")
        return self


class BorrowRecordOut(BaseSchema):
    """借用记录响应模型"""
    id: int = Field(..., description="借用记录 ID")
    user_id: int = Field(..., description="借用用户 ID")
    equipment_id: int = Field(..., description="设备 ID")
    borrow_start_time: datetime = Field(..., description="借用开始时间")
    borrow_end_time: datetime = Field(..., description="借用结束时间")
    purpose: str | None = Field(None, description="借用用途")
    status: str = Field(..., description="借用状态")
    review_remark: str | None = Field(None, description="审核备注")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

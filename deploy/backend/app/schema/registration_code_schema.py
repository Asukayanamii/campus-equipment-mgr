from datetime import datetime

from fastapi_pagination import Params
from pydantic import AliasChoices, Field, field_validator, model_validator

from app.constant.status_constant import REGISTRATION_CODE_TYPE_CODES
from app.core.exceptions import BussinessException
from app.schema.base_schema import BaseSchema


class RegistrationCodeCreate(BaseSchema):
    code: str = Field(
        ...,
        min_length=1,
        max_length=128,
        validation_alias=AliasChoices("code", "registration_code", "registrationCode"),
        description="plain registration code",
    )
    code_type: str = Field(..., description="注册码适用账号类型")

    @field_validator("code_type")
    def validate_code_type(cls, value: str):
        if value not in REGISTRATION_CODE_TYPE_CODES:
            raise BussinessException("注册码类型不正确", status_code=422)
        return value


class RegistrationCodeUpdate(BaseSchema):
    code: str | None = Field(
        None,
        min_length=1,
        max_length=128,
        validation_alias=AliasChoices("code", "registration_code", "registrationCode"),
        description="plain registration code",
    )
    code_type: str | None = Field(None, description="注册码适用账号类型")
    is_used: bool | None = Field(None, description="是否已使用")

    @field_validator("code_type")
    def validate_code_type(cls, value: str | None):
        if value is not None and value not in REGISTRATION_CODE_TYPE_CODES:
            raise BussinessException("注册码类型不正确", status_code=422)
        return value

    @model_validator(mode="after")
    def validate_update_fields(self):
        if not self.model_fields_set:
            raise ValueError("at least one field is required")
        return self


class RegistrationCodeQuery(BaseSchema, Params):
    is_used: bool | None = Field(None, description="whether used")
    code_type: str | None = Field(None, description="注册码适用账号类型")

    @field_validator("code_type")
    def validate_code_type(cls, value: str | None):
        if value is not None and value not in REGISTRATION_CODE_TYPE_CODES:
            raise BussinessException("注册码类型不正确", status_code=422)
        return value


class RegistrationCodeOut(BaseSchema):
    id: int
    code: str
    code_type: str
    is_used: bool
    create_time: datetime
    update_time: datetime

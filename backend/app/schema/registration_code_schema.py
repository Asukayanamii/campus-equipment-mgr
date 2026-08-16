from datetime import datetime

from fastapi_pagination import Params
from pydantic import AliasChoices, Field, model_validator

from app.schema.base_schema import BaseSchema


class RegistrationCodeCreate(BaseSchema):
    code: str = Field(
        ...,
        min_length=1,
        max_length=128,
        validation_alias=AliasChoices("code", "registration_code", "registrationCode"),
        description="plain registration code",
    )


class RegistrationCodeUpdate(BaseSchema):
    code: str | None = Field(
        None,
        min_length=1,
        max_length=128,
        validation_alias=AliasChoices("code", "registration_code", "registrationCode"),
        description="plain registration code",
    )
    is_used: bool | None = Field(None, description="whether used")

    @model_validator(mode="after")
    def validate_update_fields(self):
        if not self.model_fields_set:
            raise ValueError("at least one field is required")
        return self


class RegistrationCodeQuery(BaseSchema, Params):
    is_used: bool | None = Field(None, description="whether used")


class RegistrationCodeOut(BaseSchema):
    id: int
    code: str
    is_used: bool
    create_time: datetime
    update_time: datetime

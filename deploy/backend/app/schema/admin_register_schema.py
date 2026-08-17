from pydantic import AliasChoices, Field

from app.schema.common_schema import InfoRegexBaseSchema


class AdminRegisterIn(InfoRegexBaseSchema):
    username: str = Field(..., description="username")
    password: str = Field(..., description="password")
    registration_code: str = Field(
        ...,
        min_length=1,
        max_length=128,
        validation_alias=AliasChoices("registration_code", "registrationCode", "code"),
        description="registration code",
    )

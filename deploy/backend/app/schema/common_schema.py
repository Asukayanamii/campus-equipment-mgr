import re
from datetime import datetime

from fastapi_pagination import Params
from pydantic import Field, field_validator, model_validator

from app.constant.regex_constant import RegexConstant
from app.core.exceptions import BussinessException
from app.schema.base_schema import BaseSchema



class PageQuery(BaseSchema, Params):
    page: int = Field(default=1, ge=1, le=1000, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页条数")


class InfoRegexBaseSchema(BaseSchema):
    """正则表达式校验"""
    # 用户名正则校验
    @field_validator("username",check_fields= False)
    def validate_username(cls, value: str):
        if not re.fullmatch(RegexConstant.USERNAME, value):
            raise BussinessException("用户名仅支持中文、大小写字母、数字、下划线，长度6~24位",status_code=422)
        return value

    # 密码完整正则校验（包含前瞻断言，使用Python原生re）
    @field_validator("password",check_fields= False)
    def validate_password(cls, value: str | None):
        if value is not None and not re.fullmatch(RegexConstant.PASSWORD, value):
            raise BussinessException("密码必须同时包含字母和数字，仅允许字母、数字、_!@#$%^&*()-=，长度6~24位",status_code=422)
        return value

    @field_validator("new_password", check_fields=False)
    def validate_new_password(cls, value: str | None):
        if value is not None and not re.fullmatch(RegexConstant.PASSWORD, value):
            raise BussinessException("新密码必须同时包含字母和数字，仅允许字母、数字、_!@#$%^&*()-=，长度6~24位", status_code=422)
        return value
    # 姓名正则校验
    @field_validator("name",check_fields= False)
    def validate_name(cls, value: str):
        if not re.fullmatch(RegexConstant.NAME, value):
            raise BussinessException("姓名仅支持中文、字母、数字、下划线、短横，长度2~12位",status_code=422)
        return value
    # 邮箱专属校验器
    @field_validator("email",check_fields= False)
    def validate_email(cls, value: str):
        if not re.fullmatch(RegexConstant.EMAIL, value):
            raise BussinessException("邮箱格式不正确，请输入合法邮箱地址，例如：xxx@xxx.com",422)
        return value

# 注册、登录、修改信息通用基础模型
class RegisterIn(InfoRegexBaseSchema):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class AdminRegisterIn(RegisterIn):
    registration_code: str = Field(..., min_length=1, max_length=100, description="管理员注册码")

class LoginIn(InfoRegexBaseSchema):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class EmailVerificationCodeIn(InfoRegexBaseSchema):
    """学生邮箱验证码发送请求。"""
    email: str = Field(..., description="邮箱")


class EmailLoginIn(InfoRegexBaseSchema):
    """学生邮箱验证码注册并登录请求。"""
    email: str = Field(..., description="邮箱")
    verification_code: str = Field(..., min_length=6, max_length=6, description="六位邮箱验证码")


class EmailBindingIn(InfoRegexBaseSchema):
    """学生校验邮箱验证码并绑定邮箱的请求。"""

    email: str = Field(..., description="待绑定邮箱")
    verification_code: str = Field(..., pattern=r"^\d{6}$", description="六位邮箱验证码")


class EmailLoginOut(BaseSchema):
    """学生邮箱验证码注册或登录成功响应。"""
    id: int = Field(..., description="用户 ID")
    name: str = Field(..., description="昵称")
    username: str = Field(..., description="系统生成的账号")
    image: str | None = Field(None, description="头像图片 URL")
    email: str = Field(..., description="邮箱")
    token: str = Field(..., description="登录令牌")


class LoginOut(InfoRegexBaseSchema):
    """登录成功返回结果"""
    id: int = Field(..., description="用户id")
    name: str = Field(description="昵称")
    token: str = Field(..., description="登录成功返回的token")
    username: str = Field(..., description="用户名")

class UpdateIn(InfoRegexBaseSchema):
    id: int = Field(..., description="用户id")
    name: str = Field(..., description="昵称")
    password: str | None = Field(None, description="原密码")
    new_password: str | None = Field(None, description="新密码")
    image: str | None = Field(None, description="头像图片 URL")

    @model_validator(mode="after")
    def validate_password_update(self):
        if (self.password is None) != (self.new_password is None):
            raise ValueError("修改密码时必须同时提供原密码和新密码")
        return self

class UpdateInDTO(InfoRegexBaseSchema):
    name: str = Field(..., description="昵称")
    password: str | None = Field(None, description="原密码")
    new_password: str | None = Field(None, description="新密码")
    image: str | None = Field(None, description="头像图片 URL")

    @model_validator(mode="after")
    def validate_password_update(self):
        if (self.password is None) != (self.new_password is None):
            raise ValueError("修改密码时必须同时提供原密码和新密码")
        return self

# 获取当前用户信息响应模型
class GetMeOut(BaseSchema):
    id: int = Field(..., description="用户id")
    name: str = Field(...,description="昵称")
    username: str = Field(..., description="用户名")
    image: str | None = Field(None, description="头像图片 URL")
    email: str | None = Field(None, description="邮箱")
    update_time: datetime = Field(..., description="更新时间")
    create_time: datetime = Field(..., description="创建时间")

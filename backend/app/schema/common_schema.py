import re
from datetime import datetime

from pydantic import Field, field_validator

from app.constant.regex_constant import RegexConstant
from app.core.exceptions import BussinessException
from app.schema.base_schema import BaseSchema



class PageQuery(BaseSchema):
    page: int = Field(default=1, ge=1, le=1000)
    size: int = Field(default=10, ge=1, le=100)


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
    def validate_password(cls, value: str):
        if not re.fullmatch(RegexConstant.PASSWORD, value):
            raise BussinessException("密码必须同时包含字母和数字，仅允许字母、数字、_!@#$%^&*()-=，长度6~24位",status_code=422)
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

class LoginIn(InfoRegexBaseSchema):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class LoginOut(InfoRegexBaseSchema):
    """登录成功返回结果"""
    id: int = Field(..., description="用户id")
    name: str = Field(description="昵称")
    token: str = Field(..., description="登录成功返回的token")
    username: str = Field(..., description="用户名")

class UpdateIn(InfoRegexBaseSchema):
    id: int = Field(..., description="用户id")
    name: str = Field(..., description="昵称")
    password: str = Field(..., description="密码")
    image: str | None = Field(None, description="头像")

class UpdateInDTO(InfoRegexBaseSchema):
    name: str = Field(..., description="昵称")
    password: str = Field(..., description="密码")
    image: str | None = Field(None, description="头像")

# 获取当前用户信息响应模型
class GetMeOut(BaseSchema):
    id: int = Field(..., description="用户id")
    name: str = Field(...,description="昵称")
    username: str = Field(..., description="用户名")
    image: str | None = Field(None, description="头像")
    email: str | None = Field(None, description="邮箱")
    update_time: datetime = Field(..., description="更新时间")
    create_time: datetime = Field(..., description="创建时间")
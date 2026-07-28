from pydantic import BaseModel,Field


class RegisterIn(BaseModel):
    username: str = Field(..., description="用户名", min_length=8, max_length=24)
    password: str = Field(..., description="密码",min_length=8, max_length=24)

class LoginIn(BaseModel):
    username: str = Field(..., description="用户名", min_length=8, max_length=24)
    password: str = Field(..., description="密码",min_length=8, max_length=24)

class LoginOut(BaseModel):
    """登录成功返回结果"""
    id: int = Field(..., description="用户id")
    name: str |  None = Field(description="姓名")
    token: str = Field(..., description="登录成功返回的token")
    username: str = Field(..., description="用户名")
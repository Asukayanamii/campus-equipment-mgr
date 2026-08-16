from pydantic import BaseModel, Field
from typing import TypeVar,Generic,Optional
from fastapi.responses import JSONResponse
from app.constant.result_constant import ResultCode

T=TypeVar('T')

class Result(BaseModel,Generic[T]):
    """
    统一返回结果类
    """
    code: int = Field(..., description="业务状态码")
    message: str = Field(..., description="响应消息")
    data: T | None = Field(None, description="响应数据")

    @classmethod
    def success(cls,data: T|None = None,message: str = "success",code: int = ResultCode.SUCCESS_CODE)->'Result[T]':
        """
        操作成功
        """
        return cls(message=message, data=data, code=code)
    @classmethod
    def fail(cls,message: str = "fail",code: int = ResultCode.FAIL_CODE)->'Result[T]':
        """
        操作失败
        """
        return cls(message=message, code=code)

    # 新增：直接返回响应对象
    def to_json(self,code: int = 200) -> JSONResponse:
        return JSONResponse(content=self.model_dump(), status_code=code)


class ErrorResult(BaseModel):
    """全局异常处理器返回的统一错误响应，用于 OpenAPI 文档。"""

    code: int = Field(ResultCode.FAIL_CODE, description="业务状态码，失败时固定为 1")
    message: str = Field(..., description="错误信息")
    data: None = Field(None, description="错误响应不返回业务数据")

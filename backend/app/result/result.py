from pydantic import BaseModel
from typing import TypeVar,Generic,Optional
from fastapi.responses import JSONResponse
from app.constant.result_constant import ResultCode

T=TypeVar('T')

class Result(BaseModel,Generic[T]):
    """
    统一返回结果类
    """
    code: int
    message: str
    data: T | None = None

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
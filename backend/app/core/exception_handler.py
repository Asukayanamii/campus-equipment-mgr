from fastapi.exceptions import RequestValidationError

from app.core.exceptions import BussinessException
from app.core.logger import logger
from app.result.result import Result
from fastapi import Request

def register_exception_handler(app):
    """
    业务异常处理
    """
    @app.exception_handler(BussinessException)
    async def bussiness_exception_handler(request: Request, exc: BussinessException):
        logger.error(f"{request.method} {request.url} {exc}")
        return Result.fail(str(exc)).to_json(code=exc.status_code)

    # 重写参数校验422异常处理器（覆盖内置）
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # 提取pydantic校验错误信息
        err_details = []
        for err in exc.errors():
            loc = ".".join(map(str, err["loc"]))
            err_details.append(f"字段 {loc}: {err['msg']}")

        return Result.fail("；".join(err_details)).to_json(code=422)


    """
    注册全局异常处理
    """
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        logger.error(f"{request.method} {request.url} {exc}")
        return Result.fail(str(exc)).to_json(code=500)

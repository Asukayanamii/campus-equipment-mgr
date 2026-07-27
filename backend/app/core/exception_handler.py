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
    """
    注册全局异常处理
    """
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        logger.error(f"{request.method} {request.url} {exc}")
        return Result.fail(str(exc)).to_json(code=500)

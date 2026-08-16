from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.result.result import ErrorResult

ERROR_RESPONSES: dict[str, dict[str, str]] = {
    "400": {"description": "请求参数或当前业务状态不合法", "message": "当前操作不允许执行"},
    "401": {"description": "未登录、登录已过期或身份不匹配", "message": "未登录，请先登录"},
    "403": {"description": "当前账号没有执行该操作的权限", "message": "无权限执行此操作"},
    "404": {"description": "请求的接口或业务资源不存在", "message": "设备不存在"},
    "405": {"description": "请求方法不被当前接口支持", "message": "Method Not Allowed"},
    "409": {"description": "请求与现有资源或业务状态发生冲突", "message": "设备编号已存在"},
    "422": {"description": "请求参数校验失败", "message": "字段 body.field: 输入不合法"},
    "429": {"description": "请求频率超过限制", "message": "验证码已发送，请在有效期结束后再试"},
    "500": {"description": "服务内部异常或外部服务配置不完整", "message": "服务器内部错误"},
    "503": {"description": "依赖服务暂不可用", "message": "验证码服务暂不可用"},
}

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def _error_response(definition: dict[str, str]) -> dict[str, Any]:
    """构造与全局异常处理器一致的错误响应文档。"""
    return {
        "description": definition["description"],
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/ErrorResult"},
                "example": {
                    "code": 1,
                    "message": definition["message"],
                    "data": None,
                },
            }
        },
    }


def create_custom_openapi(app: FastAPI) -> Callable[[], dict[str, Any]]:
    """为全部接口注入项目统一的非成功响应模型。"""

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        components = openapi_schema.setdefault("components", {})
        schemas = components.setdefault("schemas", {})
        schemas["ErrorResult"] = ErrorResult.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )

        for path_item in openapi_schema.get("paths", {}).values():
            for method, operation in path_item.items():
                if method not in HTTP_METHODS or not isinstance(operation, dict):
                    continue
                responses = operation.setdefault("responses", {})
                for status_code, definition in ERROR_RESPONSES.items():
                    # 统一覆盖 FastAPI 默认的 422 文档，确保它与全局异常处理器一致。
                    responses[status_code] = _error_response(definition)

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi

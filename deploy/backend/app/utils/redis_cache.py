import json
from collections.abc import Callable
from functools import lru_cache, wraps
from hashlib import sha256
from typing import Any, ParamSpec, TypeVar

from pydantic import BaseModel
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import logger

P = ParamSpec("P")
T = TypeVar("T", bound=BaseModel)

EQUIPMENT_CACHE_VERSION_KEY = "equipment:cache:version"
_EQUIPMENT_CACHE_INVALIDATION_FLAG = "equipment_cache_invalidation_required"


@lru_cache
def get_redis_client() -> Redis:
    """获取设备查询缓存共用的 Redis 客户端。"""
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT,
        socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
    )


def _get_equipment_cache_version() -> str:
    try:
        return get_redis_client().get(EQUIPMENT_CACHE_VERSION_KEY) or "0"
    except RedisError:
        logger.warning("Redis is unavailable when reading the equipment cache version")
        return "0"


def redis_cache(
    key_prefix: str,
    key_builder: Callable[P, dict[str, Any]],
    response_model: type[T],
    expire_seconds: int,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """缓存 Pydantic 响应对象，Redis 异常时自动回源查询。"""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key_payload = json.dumps(
                key_builder(*args, **kwargs),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            cache_key = f"{key_prefix}:v{_get_equipment_cache_version()}:{sha256(key_payload.encode()).hexdigest()}"

            try:
                cached_value = get_redis_client().get(cache_key)
                if cached_value is not None:
                    # 从缓存恢复响应模型，确保返回类型与数据库查询结果一致。
                    return response_model.model_validate_json(cached_value)
            except (RedisError, ValueError):
                logger.warning("Redis is unavailable or contains invalid equipment cache data; querying the database")

            result = func(*args, **kwargs)
            try:
                get_redis_client().setex(
                    cache_key,
                    expire_seconds,
                    result.model_dump_json(),
                )
            except RedisError:
                logger.warning("Redis is unavailable when writing the equipment query cache")
            return result

        return wrapper

    return decorator


def mark_equipment_cache_invalidation(session: Session) -> None:
    """标记当前事务，待提交成功后再更新设备缓存版本。"""
    session.info[_EQUIPMENT_CACHE_INVALIDATION_FLAG] = True


@event.listens_for(Session, "after_commit")
def invalidate_equipment_cache_after_commit(session: Session) -> None:
    """设备或分类变更提交后递增命名空间版本，使旧缓存失效。"""
    if not session.info.pop(_EQUIPMENT_CACHE_INVALIDATION_FLAG, False):
        return

    try:
        get_redis_client().incr(EQUIPMENT_CACHE_VERSION_KEY)
    except RedisError:
        logger.warning("Redis is unavailable when invalidating the equipment query cache")


@event.listens_for(Session, "after_rollback")
def discard_equipment_cache_invalidation(session: Session) -> None:
    """事务回滚时丢弃缓存失效标记。"""
    session.info.pop(_EQUIPMENT_CACHE_INVALIDATION_FLAG, None)

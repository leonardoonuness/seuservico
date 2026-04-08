import logging
import redis

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_redis_client() -> redis.Redis | None:
    """Create Redis client only when REDIS_URL is configured."""
    if not settings.REDIS_URL:
        logger.warning("REDIS_URL not configured; Redis-backed features are disabled.")
        return None

    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()
        return client
    except Exception as exc:
        logger.warning("Redis unavailable; Redis-backed features are disabled. error=%s", exc)
        return None


redis_client = _build_redis_client()


def blacklist_token(token: str, expire_seconds: int = 3600) -> None:
    if not redis_client:
        return
    redis_client.setex(f"blacklist:{token}", expire_seconds, "1")


def is_token_blacklisted(token: str) -> bool:
    if not redis_client:
        return False
    return redis_client.exists(f"blacklist:{token}") == 1


def cache_set(key: str, value: str, expire: int = 300) -> None:
    if not redis_client:
        return
    redis_client.setex(key, expire, value)


def cache_get(key: str) -> str | None:
    if not redis_client:
        return None
    return redis_client.get(key)


def cache_delete(key: str) -> None:
    if not redis_client:
        return
    redis_client.delete(key)

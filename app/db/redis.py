import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def blacklist_token(token: str, expire_seconds: int = 3600) -> None:
    redis_client.setex(f"blacklist:{token}", expire_seconds, "1")


def is_token_blacklisted(token: str) -> bool:
    return redis_client.exists(f"blacklist:{token}") == 1


def cache_set(key: str, value: str, expire: int = 300) -> None:
    redis_client.setex(key, expire, value)


def cache_get(key: str) -> str | None:
    return redis_client.get(key)


def cache_delete(key: str) -> None:
    redis_client.delete(key)

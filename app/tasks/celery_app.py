from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "seuservico",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.notifications", "app.tasks.cleanup"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
    beat_schedule={
        "cleanup-expired-tokens-daily": {
            "task": "app.tasks.cleanup.cleanup_expired_tokens",
            "schedule": 86400.0,  # every 24h
        },
    },
)

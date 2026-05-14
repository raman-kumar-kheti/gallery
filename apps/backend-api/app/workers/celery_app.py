from celery import Celery
from app.config import settings

# Backend-side Celery app used only for SENDING tasks to the ai-worker queue.
# Task definitions live in apps/ai-worker/worker/tasks/.
celery_app = Celery(
    "gallery",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,  # Ack after task completes (retry-safe)
    worker_prefetch_multiplier=1,
    task_routes={
        "app.tasks.*": {"queue": "ai_processing"},
    },
    task_default_queue="ai_processing",
)

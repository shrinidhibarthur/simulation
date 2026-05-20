from celery import Celery
from app.config import settings

celery_app = Celery(
    "simulation",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.simulation_task"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=300,
    task_time_limit=360,
    result_expires=86400,
)

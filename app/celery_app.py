from celery import Celery
from app.config import settings
import platform

# Create Celery instance and configure broker (Redis)
celery = Celery(
    "apify_scrape_social",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Windows-specific configuration
if platform.system().lower() == 'windows':
    # Use eventlet pool for Windows compatibility
    celery.conf.update(
        task_always_eager=False,
        task_eager_propagates=True,
        worker_pool_restarts=True,
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_disable_rate_limits=True,
        worker_max_tasks_per_child=1,
        worker_max_memory_per_child=200000,  # 200MB
        worker_send_task_events=True,
        task_send_sent_event=True,
        event_queue_expires=60,
        worker_pool='solo',  # Use solo pool for Windows
    )

# Autodiscover tasks in the app.tasks module
celery.autodiscover_tasks(['app']) 
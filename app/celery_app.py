from celery import Celery
from app.config import settings

# Create Celery instance and configure broker (Redis)
celery = Celery(
    "apify_scrape_social",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Autodiscover tasks in the app.tasks module
celery.autodiscover_tasks(['app']) 
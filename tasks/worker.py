from app.celery_app import celery

# This file allows you to run: celery -A tasks.worker.celery worker --loglevel=info
# Or, if you prefer, celery -A app.tasks.celery worker --loglevel=info

if __name__ == "__main__":
    celery.start() 
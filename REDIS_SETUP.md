# Redis Setup Guide

## Option 1: Redis Cloud (Recommended - Free)

1. Go to https://redis.com/try-free/
2. Sign up for free account
3. Create a new database
4. Copy the connection string
5. Update your `.env` file:

```env
REDIS_URL=redis://username:password@host:port
```

## Option 2: Docker (If you have Docker)

```bash
docker run -d -p 6379:6379 redis:latest
```

## Option 3: Windows Redis (Complex)

1. Download Redis for Windows from: https://github.com/microsoftarchive/redis/releases
2. Install and start the service

## Option 4: Disable Celery Temporarily

If you want to test without Redis, modify `app/main.py`:

```python
# Comment out this line temporarily:
# process_apify_run.delay(request_id, run_id, dataset_id)
```

## Quick Test

After setting up Redis, test with:

```bash
# Terminal 1: Start Redis (if local)
redis-server

# Terminal 2: Start Celery Worker
celery -A app.celery_app.celery worker --loglevel=info

# Terminal 3: Start your app
python run.py
``` 
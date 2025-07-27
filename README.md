# Apify Social Scraper Backend

A production-ready FastAPI backend for social media scraping using Apify, Celery, and Supabase. Includes a minimal Bootstrap UI for submitting scrape jobs, viewing statuses, and displaying results.

---

## Features
- **FastAPI** backend (async, modern, easy to extend)
- **Celery + Redis** for background job processing
- **Supabase** for storing job metadata and results
- **Minimal Bootstrap UI** (no JS required)
- **.env** for secrets (see `.env.example`)
- **SQLite fallback** for local dev (if you don't want to use Supabase)

---

## Project Structure

```
app/
    main.py           # FastAPI app, routes, web UI
    celery_app.py     # Celery config
    tasks.py          # Celery background tasks
    apify_utils.py    # Apify integration helpers
    supabase_utils.py # Supabase integration helpers
    models.py         # Pydantic models & DB schema helpers
    config.py         # Env loading, settings

templates/
    base.html
    index.html        # Form to submit scrape jobs
    jobs.html         # List job statuses
    results.html      # Show scraped results

static/
    (Bootstrap CSS, logo, etc.)

tasks/
    worker.py         # Celery worker runner

.env.example         # Example env vars
requirements.txt     # All dependencies
run.py               # Local dev launcher
README.md            # This file
```

---

## Quickstart (Local)

1. **Clone the repo**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Copy and edit your .env**
   ```bash
   cp .env.example .env
   # Fill in your APIFY_TOKEN, SUPABASE_URL, SUPABASE_KEY, etc.
   ```
4. **Create Supabase tables** (see schema below)
5. **Start Redis** (for Celery)
   ```bash
   # On Windows: use Docker Desktop or install Redis from https://github.com/microsoftarchive/redis/releases
   redis-server
   ```
6. **Start Celery worker**
   ```bash
   celery -A app.tasks.celery worker --loglevel=info
   ```
7. **Run the app**
   ```bash
   python run.py
   # Visit http://localhost:8000
   ```

---

## Supabase Table Schema

You need two tables:

### 1. scrape_jobs
| Column         | Type          | Notes                       |
| -------------- | ------------- | --------------------------- |
| id             | uuid (PK)     | auto-generated              |
| platform       | text          | e.g. 'instagram', 'twitter' |
| keyword        | text          | URL or keyword              |
| frequency      | text          | e.g. 'daily', 'once'        |
| run_id         | text          | Apify run ID                |
| status         | text          | pending/running/complete    |
| created_at     | timestamptz   | default now()               |
| updated_at     | timestamptz   |                             |

### 2. scrape_results
| Column         | Type          | Notes                       |
| -------------- | ------------- | --------------------------- |
| id             | uuid (PK)     | auto-generated              |
| job_id         | uuid (FK)     | references scrape_jobs(id)  |
| data           | jsonb         | scraped & processed data    |
| created_at     | timestamptz   | default now()               |

---

## Deploying on PythonAnywhere (Free Tier)

1. Upload your code to PythonAnywhere.
2. Create a virtualenv and install requirements:
   ```bash
   mkvirtualenv myenv --python=python3.10
   pip install -r requirements.txt
   ```
3. Set up your `.env` in your home directory.
4. [Enable ASGI support](https://help.pythonanywhere.com/pages/ASGICommandLine) (request if not enabled).
5. Use this command to run FastAPI:
   ```bash
   /home/YOURUSERNAME/.virtualenvs/myenv/bin/uvicorn --app-dir /home/YOURUSERNAME/Apify_Scrape_social/app --uds ${DOMAIN_SOCKET} main:app
   ```
6. Set up a Redis instance (use a free cloud Redis if needed, or run locally for dev).
7. Start Celery worker in a console:
   ```bash
   celery -A app.tasks.celery worker --loglevel=info
   ```
8. Visit your PythonAnywhere subdomain.

---

## Deploying on Google Cloud (Compute Engine)

1. Create a VM (Ubuntu recommended).
2. Install Python 3.10+, Redis, and git.
3. Clone your repo and set up a virtualenv.
4. Install requirements and set up `.env`.
5. Use systemd or Docker to run Uvicorn and Celery (see [CodeArmo FastAPI deploy guide](https://www.codearmo.com/python-tutorial/ultimate-guide-deploy-fastapi-app-nginx-linux)).
6. Set up Nginx as a reverse proxy for production.

---

## Usage
- Go to `/` to submit a new scrape job.
- `/jobs` to see job statuses.
- `/results/{job_id}` to see results.

---

## Credits
- [Apify Python Client](https://github.com/apify/apify-client-python)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Celery](https://docs.celeryq.dev/)

---

## License
MIT 
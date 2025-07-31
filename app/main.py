from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.models import CompetitorMonitorRequest
from app.apify_utils import start_apify_actor
from app.supabase_utils import insert_scrape_request, fetch_all_requests, fetch_results_for_request, fetch_request_data
from app.tasks import process_apify_run
import os
import logging
import subprocess
import sys
import threading
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to track Celery worker process
celery_process = None

def start_celery_worker():
    """Start Celery worker in a separate thread"""
    global celery_process
    try:
        logger.info("Starting Celery worker...")
        celery_process = subprocess.Popen([
            sys.executable, "-m", "celery", 
            "-A", "app.celery_app.celery", 
            "worker", 
            "--loglevel=info",
            "--pool=solo"
        ])
        logger.info("Celery worker started successfully")
    except Exception as e:
        logger.error(f"Failed to start Celery worker: {e}")

def stop_celery_worker():
    """Stop Celery worker"""
    global celery_process
    if celery_process:
        logger.info("Stopping Celery worker...")
        celery_process.terminate()
        celery_process.wait()
        logger.info("Celery worker stopped")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI startup and shutdown"""
    # Startup
    logger.info("Starting application...")
    celery_thread = threading.Thread(target=start_celery_worker, daemon=True)
    celery_thread.start()
    # Give Celery a moment to start
    time.sleep(3)
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    stop_celery_worker()
    logger.info("Application shutdown complete")

app = FastAPI(
    title='Social Media Scraper',
    docs_url='/docs',
    lifespan=lifespan,
)

# Mount static files (Bootstrap, etc.)
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), '..', 'templates'))

@app.get("/")
def index(request: Request):
    """
    Render the add competitor monitoring form.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/add-monitor")
def add_monitor(request: Request, platform: str = Form(...), competitor: str = Form(...), frequency: str = Form(...)):
    """
    Handle form submission to add a new competitor monitor.
    """
    try:
        logger.info(f"Starting new monitor for platform: {platform}, competitor: {competitor}, frequency: {frequency}")

        # For demo: use a generic actor (user should customize this)
        actor_id = "shu8hvrXbJbY3Eb9W"  # Example actor
        run_input = {
            'addParentData': False,
            'directUrls': [
                    competitor
                ],
            'enhanceUserSearchWithFacebookPage': False,
            'isUserReelFeedURL': False,
            'isUserTaggedFeedURL': False,
            'resultsLimit': 2,
            'resultsType': 'posts',
            'searchLimit': 1,
            'searchType': 'hashtag'
            }

        # Start actor immediately (non-blocking)
        logger.info(f"Starting Apify actor: {actor_id}")
        run = start_apify_actor(actor_id, run_input)
        run_id = run["id"]
        dataset_id = run["defaultDatasetId"]
        logger.info(f"Apify run started - run_id: {run_id}, dataset_id: {dataset_id}")

        # Insert monitor in Supabase
        request_id = insert_scrape_request(platform, competitor, frequency, run_id, status="pending")
        logger.info(f"Request inserted with ID: {request_id}")

        # Queue background task to poll and process results
        logger.info(f"Queuing background task for request_id: {request_id}")
        process_apify_run.delay(request_id, run_id, dataset_id)

        return RedirectResponse(url="/requests", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        logger.error(f"Error in add_monitor: {str(e)}", exc_info=True)
        raise

@app.get("/requests")
def all_results(request: Request):
    """
    Show all active competitor monitors and their statuses.
    """
    monitors = fetch_all_requests()
    return templates.TemplateResponse("requests.html", {"request": request, "monitors": monitors})


@app.get("/requests/{request_id}")
def get_result(request: Request, request_id: str):
    """
    Show results for a given competitor monitor.
    """
    request_data = fetch_request_data(request_id)
    results = fetch_results_for_request(request_id)
    return templates.TemplateResponse("results.html", {"request": request, "results": results, 'request_data': request_data}) 
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.models import CompetitorMonitorRequest
from app.apify_utils import start_apify_actor
from app.supabase_utils import (
    insert_scrape_request, fetch_all_requests, fetch_results_for_request, fetch_request_data, insert_request_run_id
)
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

app = FastAPI(
    title='Social Media Scraper',
    docs_url='/docs',
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

        actor_id = "shu8hvrXbJbY3Eb9W"  # Example actor
        run_input = {
            'addParentData': False,
            'directUrls': [competitor],
            'enhanceUserSearchWithFacebookPage': False,
            'isUserReelFeedURL': False,
            'isUserTaggedFeedURL': False,
            'resultsLimit': 2,
            'resultsType': 'posts',
            'searchLimit': 1,
            'searchType': 'hashtag'
            }

        # Insert monitor in Supabase
        request_id = insert_scrape_request(platform, competitor, frequency, run_id=None, status="pending")
        logger.info(f"Request inserted with ID: {request_id}")

        # Start actor immediately (non-blocking)
        logger.info(f"Starting Apify actor: {actor_id}")
        run = start_apify_actor(actor_id, run_input)
        run_id = run["id"]
        dataset_id = run["defaultDatasetId"]
        logger.info(f"Apify run started - run_id: {run_id}, dataset_id: {dataset_id}")

        # Insert run_id in Supabase request
        insert_request_run_id(request_id, run_id)
        logger.info(f"run_id: {run_id} inserted for request_id: {request_id}")

        return RedirectResponse(url="/requests", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        logger.error(f"Error in add_monitor: {str(e)}", exc_info=True)
        raise

@app.post("/webhook/apify")
def apify_webhook(request: Request, payload: dict):

    # payload will have at least runId and eventType
    run_id = payload["runId"]
    request_id = fetch_request_data(run_id=run_id).get('id')
    logger.info(f"From apify_webhook: {payload}")
    
    # Process Apify run upon finish
    process_apify_run(request_id, run_id)

    return JSONResponse({'data': payload}, status_code=200)

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
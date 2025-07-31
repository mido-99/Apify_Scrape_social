from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models import CompetitorMonitorRequest
from app.apify_utils import start_apify_actor
from app.supabase_utils import insert_scrape_request, fetch_all_requests, fetch_results_for_request, fetch_request_data
from app.tasks import process_apify_run
import os

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
    run = start_apify_actor(actor_id, run_input)
    run_id = run["id"]
    dataset_id = run["defaultDatasetId"]
    # Insert monitor in Supabase
    request_id = insert_scrape_request(platform, competitor, frequency, run_id, status="pending")
    # Queue background task to poll and process results
    process_apify_run.delay(request_id, run_id, dataset_id)
    return RedirectResponse(url="/requests", status_code=status.HTTP_303_SEE_OTHER)

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
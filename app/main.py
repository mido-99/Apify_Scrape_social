from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models import ScrapeJobRequest
from app.apify_utils import start_apify_actor
from app.supabase_utils import insert_scrape_job, fetch_all_jobs, fetch_results_for_job
from app.tasks import process_apify_run
import os

app = FastAPI()

# Mount static files (Bootstrap, etc.)
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), '..', 'templates'))

@app.get("/")
def index(request: Request):
    """
    Render the scrape job submission form.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit")
def submit_job(request: Request, platform: str = Form(...), keyword: str = Form(...), frequency: str = Form(...)):
    """
    Handle form submission, start Apify actor, insert job, and queue Celery task.
    """
    # For demo: use a generic actor (user should customize this)
    actor_id = "apify/instagram-followers-count-scraper"  # Example actor
    run_input = {"usernames": [keyword]}  # Adjust for your actor
    run = start_apify_actor(actor_id, run_input)
    run_id = run["id"]
    dataset_id = run["defaultDatasetId"]
    # Insert job in Supabase
    job_id = insert_scrape_job(platform, keyword, frequency, run_id, status="pending")
    # Queue background task
    process_apify_run.delay(job_id, run_id, dataset_id)
    return RedirectResponse(url="/jobs", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/jobs")
def jobs(request: Request):
    """
    Show all scrape jobs and their statuses.
    """
    jobs = fetch_all_jobs()
    return templates.TemplateResponse("jobs.html", {"request": request, "jobs": jobs})

@app.get("/results/{job_id}")
def results(request: Request, job_id: str):
    """
    Show results for a given job.
    """
    results = fetch_results_for_job(job_id)
    return templates.TemplateResponse("results.html", {"request": request, "results": results}) 
from supabase import create_client
from app.config import settings
from uuid import uuid4
from datetime import datetime

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Insert a new scrape job into Supabase
def insert_scrape_job(platform, keyword, frequency, run_id, status):
    """
    Inserts a new scrape job row and returns the job id.
    """
    job_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    data = {
        "id": job_id,
        "platform": platform,
        "keyword": keyword,
        "frequency": frequency,
        "run_id": run_id,
        "status": status,
        "created_at": now,
        "updated_at": now,
    }
    supabase.table("scrape_jobs").insert(data).execute()
    return job_id

# Update job status in Supabase
def update_job_status(job_id, status):
    """
    Updates the status and updated_at of a job.
    """
    now = datetime.utcnow().isoformat()
    supabase.table("scrape_jobs").update({"status": status, "updated_at": now}).eq("id", job_id).execute()

# Insert scrape results into Supabase
def insert_scrape_result(job_id, data):
    """
    Inserts a new result row for a job.
    """
    result_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    supabase.table("scrape_results").insert({
        "id": result_id,
        "job_id": job_id,
        "data": data,
        "created_at": now,
    }).execute()
    return result_id

# Fetch all jobs
def fetch_all_jobs():
    """
    Returns all jobs for display in the UI.
    """
    res = supabase.table("scrape_jobs").select("*").order("created_at", desc=True).execute()
    return res.data

# Fetch results for a job
def fetch_results_for_job(job_id):
    """
    Returns all results for a given job.
    """
    res = supabase.table("scrape_results").select("*").eq("job_id", job_id).order("created_at", desc=True).execute()
    return res.data 
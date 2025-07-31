from supabase import create_client
from app.config import settings
from datetime import datetime, timezone
from uuid import uuid4

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Insert a new scrape job into Supabase
def insert_scrape_request(platform, competitor, frequency, run_id, status):
    """
    Inserts a new scrape request row and returns the request id.
    """
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "platform": platform,
        "competitor": competitor,
        "frequency": frequency,
        "run_id": run_id,
        "status": status,
        "created_at": now,
        "updated_at": now,
    }
    query_data = supabase.table("scrape_requests").insert(data).execute()
    request_id = str(query_data.data[0]['id'])
    return request_id

def fetch_request_data(request_id):
    """
    Returns all results for a given request.
    """
    res = supabase.table("scrape_requests").select("*").eq("id", request_id).execute()
    return res.data[0]

# Update job status in Supabase
def update_request_status(request_id, status):
    """
    Updates the status and updated_at of a request.
    """
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("scrape_requests").update({"status": status, "updated_at": now}).eq("id", request_id).execute()

def process_dataset(request_id, run_id, items: list[dict]):
    """Process dataset items before saving into supabase
    """
    for dataset_item in items:
        # Remove extra fields
        if 'inputUrl' in dataset_item.keys():
            del dataset_item['inputUrl']
        # Add new keys
        dataset_item.update({
        "result_id": str(uuid4()),
        "request_id": request_id,
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        })

def insert_scrape_result(request_id, run_id, data):
    """
    Inserts a new result row for a request into Supabase.
    """
    process_dataset(request_id, run_id, data)
    supabase.table("posts").insert(data).execute()
    return True

def fetch_all_requests():
    """
    Returns all requests for display in the UI.
    """
    res = supabase.table("scrape_requests").select("*").order("created_at", desc=True).execute()
    return res.data

# Fetch results for a request
def fetch_results_for_request(request_id):
    """
    Returns all results for a given request.
    """
    res = supabase.table("posts").select("*").eq("request_id", request_id).order("created_at", desc=True).execute()
    return res.data
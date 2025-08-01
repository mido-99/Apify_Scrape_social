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

def fetch_request_data(request_id=None, run_id=None):
    """
    Returns all results for a given request.
    """
    if run_id is not None:
        res = supabase.table("scrape_requests").select("*").eq("run_id", run_id).execute()
    else:
        res = supabase.table("scrape_requests").select("*").eq("id", request_id).execute()
    return res.data[0]

def update_request_status(request_id, status):
    """
    Updates the status and updated_at of a request.
    """
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("scrape_requests").update({"status": status, "updated_at": now}).eq("id", request_id).execute()

def insert_request_run_id(request_id, run_id):
    """
    Insert Apify run_id into Supabase request.
    """
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("scrape_requests").update({"run_id": run_id, "updated_at": now}).eq("id", request_id).execute()
    update_request_status(request_id, "running")

def process_dataset(request_id, run_id, items: list[dict]):
    """Process dataset items before saving into supabase
    """
    ALLOWED_DB_COLUMNS = {
        "id", "type", "shortCode", "caption", "url", "commentsCount", "firstComment", "dimensionsHeight", "dimensionsWidth",
        "displayUrl", "alt", "likesCount", "ownerFullName", "ownerUsername", "ownerId", "isSponsored", "paidPartnership",  
        "isCommentsDisabled", "hashtags", "mentions", "images", "latestComments",  "commentOwners", "childPosts", 'taggedUsers'
        }
    NOT_ALLOWED_COLUMNS = {'inputUrl'}
    
    for dataset_item in items:
        # Remove extra fields
        keys_to_remove = [key for key in dataset_item if key in NOT_ALLOWED_COLUMNS or key not in ALLOWED_DB_COLUMNS]
        for key in keys_to_remove:
            dataset_item.pop(key, None)
        # Add new fields
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
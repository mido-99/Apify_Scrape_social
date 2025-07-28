from app.celery_app import celery
from app.apify_utils import poll_apify_run, fetch_apify_dataset_items
from app.supabase_utils import update_request_status, insert_scrape_result

@celery.task
def process_apify_run(request_id, run_id, dataset_id):
    """
    Celery background task to poll Apify run, fetch results, and store in Supabase.
    """
    # 1. Poll Apify run until finished
    update_request_status(request_id, "running")
    run = poll_apify_run(run_id)
    if run["status"] == "SUCCEEDED":
        # 2. Fetch dataset items
        items = fetch_apify_dataset_items(dataset_id)
        # 3. Store results in Supabase
        insert_scrape_result(request_id, items)
        update_request_status(request_id, "complete")
    else:
        update_request_status(request_id, f"failed: {run['status']}") 
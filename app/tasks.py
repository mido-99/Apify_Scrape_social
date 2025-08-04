import logging

from app.apify_utils import poll_apify_run, fetch_apify_dataset_items
from app.supabase_utils import update_request_status, insert_scrape_result

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_apify_run(request_id, run_id):
    """
    Task to poll Apify run, fetch results, and store in Supabase.
    """
    try:
        logger.info(f"Polling Apify run: {run_id}")
        run = await poll_apify_run(run_id)
        logger.info(f"Apify run completed with status: {run['status']}")
        
        if run["status"] == "SUCCEEDED":
            # 2. Fetch dataset items
            dataset_id = run['defaultDatasetId']
            logger.info(f"From process_apify_run: {dataset_id}")
            items = await fetch_apify_dataset_items(dataset_id)
            
            # 3. Store results in Supabase
            logger.info(f"Inserting {len(items)} items into Supabase")
            insert_scrape_result(request_id, run_id, items)
            update_request_status(request_id, "complete")
            logger.info(f"Task completed successfully for request_id: {request_id}")
        else:
            error_msg = f"failed: {run['status']}"
            logger.error(f"Apify run failed with status: {run['status']}")
            update_request_status(request_id, error_msg)
            
    except Exception as e:
        logger.error(f"Error in process_apify_run task: {str(e)}", exc_info=True)
        update_request_status(request_id, f"failed: {str(e)}")
        raise 
import logging
import os, asyncio
from apify_client import ApifyClient, ApifyClientAsync
from app.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper to start an Apify actor with input and return the run info
def start_apify_actor(actor_id: str, run_input: dict) -> dict:
    """
    Starts an Apify actor and returns the run object immediately without waiting.
    """
    # base_url = 'https://' + os.environ['VERCEL_PROJECT_PRODUCTION_URL']
    base_url = 'https://43025d9ac2ed.ngrok-free.app'
    webhook_url = base_url + '/webhook/apify'
    
    client = ApifyClient(settings.APIFY_API)
    # Use start() instead of call() to avoid blocking
    run = client.actor(actor_id).start(
        run_input=run_input,
        # Webhook to send notification once finished 
        webhooks=[{
            'event_types': ['ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED', 'ACTOR.RUN.ABORTED'],
            'request_url': webhook_url,
            'payload_template': '''{
                "runId": {{resource.id}}, "status": {{resource.status}}
                }'''
        }])
    logging.info(f"""Actor started with the following:
                 - webhook URL: {webhook_url}
                 - run = {run}
                 """)
    return run

# Helper to poll Apify actor run until finished (sync version for Celery)
async def poll_apify_run(run_id: str, poll_interval: int = 10) -> dict:
    """
    Polls the Apify run until it finishes. Returns the final run object.
    """
    client = ApifyClientAsync(settings.APIFY_API)
    while True:
        run = await client.run(run_id).get()
        if run['status'] in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):  # Terminal states
            return run
        await asyncio.sleep(poll_interval)

# Helper to fetch dataset items from a completed run
async def fetch_apify_dataset_items(dataset_id: str) -> list:
    """
    Fetches all items from the Apify dataset.
    """
    client = ApifyClientAsync(settings.APIFY_API)
    result = await client.dataset(dataset_id).list_items()
    items = result.items
    return items
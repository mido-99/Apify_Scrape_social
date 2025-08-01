import os
from apify_client import ApifyClient
from app.config import settings

# Helper to start an Apify actor with input and return the run info
def start_apify_actor(actor_id: str, run_input: dict) -> dict:
    """
    Starts an Apify actor and returns the run object immediately without waiting.
    """
    # base_url = 'https://' + os.environ['VERCEL_URL']
    base_url = 'https://c9572d71380d.ngrok-free.app'
    webhook_url = base_url + '/webhook/apify'
    
    client = ApifyClient(settings.APIFY_API)
    # Use start() instead of call() to avoid blocking
    run = client.actor(actor_id).start(
        run_input=run_input,
        # Webhook to send notification once finished 
        webhooks=[{
            'event_types': ['ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED'],
            'request_url': webhook_url,
            'payload_template': '''{
                "runId": {{resource.id}}, "status": {{resource.status}}, "datasetId": {{resource.defaultDatasetId}}
                }'''
        }])
    return run

# Helper to poll Apify actor run until finished (sync version for Celery)
def poll_apify_run(run_id: str, poll_interval: int = 10) -> dict:
    """
    Polls the Apify run until it finishes. Returns the final run object.
    """
    client = ApifyClient(settings.APIFY_API)
    while True:
        run = client.run(run_id).get()
        if run['status'] in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):  # Terminal states
            return run
        import time
        time.sleep(poll_interval)

# Helper to fetch dataset items from a completed run
def fetch_apify_dataset_items(dataset_id: str) -> list:
    """
    Fetches all items from the Apify dataset.
    """
    client = ApifyClient(settings.APIFY_API)
    items = list(client.dataset(dataset_id).iterate_items())
    return items 
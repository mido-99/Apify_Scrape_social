from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime

class ScrapeJobRequest(BaseModel):
    """
    Model for user input when submitting a new scrape job.
    """
    platform: str = Field(..., description="Social media platform, e.g. 'instagram'")
    keyword: str = Field(..., description="Competitor URL or keyword")
    frequency: str = Field(..., description="Scrape frequency, e.g. 'once', 'daily'")

class ScrapeJobStatus(BaseModel):
    """
    Model for displaying job status in the UI.
    """
    id: UUID
    platform: str
    keyword: str
    frequency: str
    run_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

class ScrapeResult(BaseModel):
    """
    Model for displaying scrape results.
    """
    id: UUID
    job_id: UUID
    data: Any
    created_at: datetime 
from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime

class CompetitorMonitorRequest(BaseModel):
    """
    Model for user input when adding a new competitor monitor.
    """
    platform: str = Field(..., description="Social media platform, e.g. 'instagram'")
    competitor: str = Field(..., description="Competitor handle, URL, or username")
    frequency: str = Field(..., description="Monitoring frequency, e.g. 'once', 'daily'")

class CompetitorMonitorStatus(BaseModel):
    """
    Model for displaying monitor status in the UI.
    """
    id: UUID
    platform: str
    competitor: str
    frequency: str
    run_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

class CompetitorAnalysisResult(BaseModel):
    """
    Model for displaying competitor analysis results.
    """
    id: UUID
    job_id: UUID
    data: Any
    created_at: datetime 
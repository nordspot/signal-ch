import uuid
from datetime import datetime

from pydantic import BaseModel


class SourceOut(BaseModel):
    id: uuid.UUID
    source_type: str
    license_status: str
    original_url: str
    original_title: str | None = None
    original_language: str | None = None
    original_published_at: datetime | None = None
    snippet: str | None = None
    attribution_text: str
    author_name: str | None = None
    publisher_reliability_score: float | None = None
    contribution_type: str | None = None

    model_config = {"from_attributes": True}

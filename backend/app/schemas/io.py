import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class IOContentBlock(BaseModel):
    type: str  # factual_core, interpretation, context, missing_voices
    content: str
    attributions: list[str] = []


class IOContent(BaseModel):
    title: str
    lead: str
    sections: list[IOContentBlock] = []
    summary: str = ""


class IOVersionOut(BaseModel):
    id: uuid.UUID
    version_number: int
    created_at: datetime
    content_de: IOContent | None = None
    content_fr: IOContent | None = None
    content_it: IOContent | None = None
    content_en: IOContent | None = None
    trigger_type: str
    review_status: str
    diff_summary: dict | None = None

    model_config = {"from_attributes": True}


class IOOut(BaseModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    status: str
    category: str
    subcategory: str | None = None
    scope: str
    canton_codes: list[str] | None = None
    confirmation_density: float | None = None
    source_diversity: float | None = None
    completeness_score: float | None = None
    bias_spectrum: dict = {}
    missing_elements: list[str] | None = None
    version_count: int = 0
    first_reported_at: datetime | None = None

    # Inline current version content
    current_version: IOVersionOut | None = None

    model_config = {"from_attributes": True}


class IOListOut(BaseModel):
    items: list[IOOut]
    total: int
    page: int
    page_size: int


class IOFilters(BaseModel):
    category: str | None = None
    scope: str | None = None
    canton: str | None = None
    status: str | None = None
    language: str = "de"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

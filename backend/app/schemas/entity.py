import uuid
from datetime import datetime

from pydantic import BaseModel


class EntityOut(BaseModel):
    id: uuid.UUID
    entity_type: str
    canonical_name: str
    names_de: list[str] | None = None
    names_fr: list[str] | None = None
    names_it: list[str] | None = None
    names_en: list[str] | None = None
    aliases: list[str] | None = None
    metadata: dict = {}
    wikidata_id: str | None = None
    mention_count: int = 0
    last_mentioned_at: datetime | None = None

    model_config = {"from_attributes": True}


class EntityRelationOut(BaseModel):
    id: uuid.UUID
    source_entity_id: uuid.UUID
    target_entity_id: uuid.UUID
    relation_type: str
    confidence: float
    valid_from: str | None = None
    valid_to: str | None = None

    model_config = {"from_attributes": True}


class EntityListOut(BaseModel):
    items: list[EntityOut]
    total: int

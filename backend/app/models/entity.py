import uuid
from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    # Classification
    entity_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="person|organization|location|law|financial_figure|concept|event|product"
        "|political_party|government_body|company|ngo|academic_institution",
    )

    # Names
    canonical_name: Mapped[str] = mapped_column(Text, nullable=False)
    names_de: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    names_fr: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    names_it: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    names_en: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    aliases: Mapped[list[str] | None] = mapped_column(ARRAY(Text))

    # Structured metadata
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    # External identifiers
    wikidata_id: Mapped[str | None] = mapped_column(Text, index=True)
    lobbywatch_id: Mapped[str | None] = mapped_column(Text)
    sogc_uid: Mapped[str | None] = mapped_column(Text, index=True)
    bfs_number: Mapped[int | None] = mapped_column(Integer)

    # Knowledge graph
    embedding = mapped_column(Vector(1024), nullable=True)
    mention_count: Mapped[int] = mapped_column(Integer, default=0)
    last_mentioned_at: Mapped[datetime | None] = mapped_column()

    # Conflict of interest data
    coi_data: Mapped[dict] = mapped_column(JSONB, default=dict)


class EntityRelation(Base):
    __tablename__ = "entity_relations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    target_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="works_for|member_of|subsidiary_of|located_in|regulates|opposes"
        "|supports|related_to|succeeded_by|preceded_by|funded_by|spouse_of"
        "|colleague_of|competitor_of|parent_org_of",
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    source_io_ids: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)))
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

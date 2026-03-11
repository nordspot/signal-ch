import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class IntelligenceObject(Base):
    __tablename__ = "intelligence_objects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        comment="draft|review|published|archived|retracted",
    )

    # Classification
    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="politics|economy|society|culture|science|sport|environment"
        "|health|education|technology|legal|infrastructure|international|local|opinion",
    )
    subcategory: Mapped[str | None] = mapped_column(Text)

    # Geographic scope
    scope: Mapped[str] = mapped_column(
        String(20),
        default="national",
        comment="international|national|cantonal|regional|communal",
    )
    canton_codes: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    commune_bfs_numbers: Mapped[list[int] | None] = mapped_column(ARRAY(Integer))

    # Quality indicators
    confirmation_density: Mapped[float | None] = mapped_column(Float)
    source_diversity: Mapped[float | None] = mapped_column(Float)
    temporal_freshness: Mapped[float | None] = mapped_column(Float)
    completeness_score: Mapped[float | None] = mapped_column(Float)
    editorial_independence: Mapped[float | None] = mapped_column(Float)

    # Bias spectrum
    bias_spectrum: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Missing elements
    missing_elements: Mapped[list[str] | None] = mapped_column(ARRAY(Text))

    # Versioning
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    version_count: Mapped[int] = mapped_column(Integer, default=0)

    # Search
    embedding = mapped_column(Vector(1024), nullable=True)

    # Timestamps
    first_reported_at: Mapped[datetime | None] = mapped_column()
    last_source_added_at: Mapped[datetime | None] = mapped_column()


class IOVersion(Base):
    __tablename__ = "io_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    io_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Content per language
    content_de: Mapped[dict | None] = mapped_column(JSONB)
    content_fr: Mapped[dict | None] = mapped_column(JSONB)
    content_it: Mapped[dict | None] = mapped_column(JSONB)
    content_en: Mapped[dict | None] = mapped_column(JSONB)

    # Trigger
    trigger_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="initial|new_source|correction|update|editorial_edit|retraction|enrichment",
    )
    trigger_source_ids: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)))

    # Diff
    diff_summary: Mapped[dict | None] = mapped_column(JSONB)

    # Editorial
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    reviewed_at: Mapped[datetime | None] = mapped_column()
    review_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        comment="pending|approved|rejected|auto_approved",
    )


class IOSource(Base):
    __tablename__ = "io_sources"

    io_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(server_default=func.now())
    relevance_score: Mapped[float] = mapped_column(Float, default=0.5)
    contribution_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="confirms|adds_detail|contradicts|provides_context|primary_source",
    )


class IOEntity(Base):
    __tablename__ = "io_entities"

    io_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    role: Mapped[str | None] = mapped_column(Text)
    sentiment: Mapped[float | None] = mapped_column(Float)
    mention_count: Mapped[int] = mapped_column(Integer, default=1)

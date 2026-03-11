import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Origin
    source_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="government|press_release|wire_service|licensed_media|rss_metadata"
        "|social_embed|citizen|open_data|academic|corporate",
    )

    # License
    license_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="public_domain|open_license|licensed|fair_use_quotation"
        "|rss_metadata_only|pending_license|unlicensed",
    )
    can_display_full_text: Mapped[bool] = mapped_column(Boolean, default=False)
    can_synthesize_from: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_link_back: Mapped[bool] = mapped_column(Boolean, default=True)

    # Content
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    original_title: Mapped[str | None] = mapped_column(Text)
    original_language: Mapped[str | None] = mapped_column(String(10))
    original_published_at: Mapped[datetime | None] = mapped_column()

    # Full text (licensed sources only)
    full_text_encrypted: Mapped[str | None] = mapped_column(Text)

    # RSS/metadata-only
    snippet: Mapped[str | None] = mapped_column(Text)

    # Attribution
    publisher_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    attribution_text: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str | None] = mapped_column(Text)

    # Reliability
    publisher_reliability_score: Mapped[float | None] = mapped_column(Float)

    # Processing
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    assigned_io_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)

    # Embedding
    embedding = mapped_column(Vector(1024), nullable=True)

    # Extracted entities
    extracted_entities: Mapped[list] = mapped_column(JSONB, default=list)

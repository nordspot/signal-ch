import uuid
from datetime import date

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Publisher(Base):
    __tablename__ = "publishers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    # Classification
    publisher_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="wire_service|national_media|regional_media|local_media|public_broadcaster"
        "|government_agency|academic|corporate|ngo|blog|social_platform|citizen",
    )
    media_group: Mapped[str | None] = mapped_column(Text)

    # Reach & reliability
    country: Mapped[str] = mapped_column(String(5), default="CH")
    languages: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    estimated_monthly_reach: Mapped[int | None] = mapped_column(Integer)
    reliability_score: Mapped[float] = mapped_column(Float, default=0.5)
    claims_verified_count: Mapped[int] = mapped_column(Integer, default=0)
    claims_contradicted_count: Mapped[int] = mapped_column(Integer, default=0)
    correction_rate: Mapped[float | None] = mapped_column(Float)

    # Licensing
    license_type: Mapped[str | None] = mapped_column(
        String(50),
        comment="wire_subscription|bilateral_license|collective_license"
        "|public_domain|rss_only|partnership|none",
    )
    license_expires_at: Mapped[date | None] = mapped_column(Date)
    license_allows_synthesis: Mapped[bool] = mapped_column(Boolean, default=False)
    license_allows_full_text: Mapped[bool] = mapped_column(Boolean, default=False)

    # Bias assessment
    political_lean: Mapped[dict] = mapped_column(JSONB, default=dict)
    editorial_independence_score: Mapped[float | None] = mapped_column(Float)

    # RSS/API endpoints
    rss_feeds: Mapped[list] = mapped_column(JSONB, default=list)
    api_endpoint: Mapped[str | None] = mapped_column(Text)
    api_key_encrypted: Mapped[str | None] = mapped_column(Text)

    # Scraping config
    scrape_config: Mapped[dict] = mapped_column(JSONB, default=dict)

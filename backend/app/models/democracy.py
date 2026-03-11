import uuid
from datetime import date, datetime

from sqlalchemy import Date, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VoteAndInitiative(Base):
    __tablename__ = "votes_and_initiatives"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    vote_type: Mapped[str] = mapped_column(String(30), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    canton: Mapped[str | None] = mapped_column(String(5))
    commune_bfs_number: Mapped[int | None] = mapped_column(Integer)

    title_de: Mapped[str | None] = mapped_column(Text)
    title_fr: Mapped[str | None] = mapped_column(Text)
    title_it: Mapped[str | None] = mapped_column(Text)
    official_url: Mapped[str | None] = mapped_column(Text)
    vote_date: Mapped[date | None] = mapped_column(Date)

    status: Mapped[str] = mapped_column(String(20), nullable=False)
    result: Mapped[dict | None] = mapped_column(JSONB)

    synthesized_io_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    pro_arguments: Mapped[dict | None] = mapped_column(JSONB)
    contra_arguments: Mapped[dict | None] = mapped_column(JSONB)
    financial_impact: Mapped[dict | None] = mapped_column(JSONB)
    historical_precedents: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)))

    curia_vista_id: Mapped[str | None] = mapped_column(Text)


class AgencyPublication(Base):
    __tablename__ = "agency_publications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    title_de: Mapped[str | None] = mapped_column(Text)
    title_fr: Mapped[str | None] = mapped_column(Text)
    title_it: Mapped[str | None] = mapped_column(Text)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    publication_date: Mapped[date | None] = mapped_column(Date)
    publication_type: Mapped[str | None] = mapped_column(String(30))

    raw_content_path: Mapped[str | None] = mapped_column(Text)
    synthesized_io_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    synthesis_status: Mapped[str] = mapped_column(String(20), default="pending")

    views_count: Mapped[int] = mapped_column(default=0)
    unique_readers: Mapped[int] = mapped_column(default=0)
    avg_reading_time_seconds: Mapped[float | None] = mapped_column()
    shares_count: Mapped[int] = mapped_column(default=0)

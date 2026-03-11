import uuid
from datetime import datetime

from sqlalchemy import Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Annotation(Base):
    __tablename__ = "annotations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    io_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    io_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    annotation_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="word|sentence|paragraph|article",
    )
    target_selector: Mapped[dict | None] = mapped_column(JSONB)

    annotation_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="fact_check|correction|context|personal_experience|expert_insight"
        "|question|counterpoint|additional_source|flag_misleading",
    )

    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_urls: Mapped[list[str] | None] = mapped_column(ARRAY(Text))

    useful_votes: Mapped[int] = mapped_column(Integer, default=0)
    not_useful_votes: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(20), default="active")
    moderation_reason: Mapped[str | None] = mapped_column(Text)

    fact_check_verdict: Mapped[str | None] = mapped_column(String(20))

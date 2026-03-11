import uuid
from datetime import datetime

from sqlalchemy import Boolean, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, POINT, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Auth
    email: Mapped[str | None] = mapped_column(Text, unique=True)
    password_hash: Mapped[str | None] = mapped_column(Text)
    auth_provider: Mapped[str | None] = mapped_column(String(20))

    # Profile
    display_name: Mapped[str | None] = mapped_column(Text)
    preferred_language: Mapped[str] = mapped_column(String(5), default="de")

    # Location
    canton: Mapped[str | None] = mapped_column(String(5))
    commune_bfs_number: Mapped[int | None] = mapped_column(Integer)

    # Subscription
    tier: Mapped[str] = mapped_column(String(20), default="free")
    stripe_customer_id: Mapped[str | None] = mapped_column(Text)
    tier_expires_at: Mapped[datetime | None] = mapped_column()

    # Personalization
    interests: Mapped[list] = mapped_column(JSONB, default=list)
    followed_entities: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)))
    followed_ios: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)))
    blind_spot_sensitivity: Mapped[float] = mapped_column(Float, default=0.5)

    # Notifications
    notification_config: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Reputation
    reputation_score: Mapped[float] = mapped_column(Float, default=0.0)
    verified_expertise: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    annotation_accuracy: Mapped[float | None] = mapped_column(Float)

    # Privacy
    data_deletion_requested_at: Mapped[datetime | None] = mapped_column()
    consent_personalization: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_analytics: Mapped[bool] = mapped_column(Boolean, default=False)

    # Admin
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_editor: Mapped[bool] = mapped_column(Boolean, default=False)


class UserIOInteraction(Base):
    __tablename__ = "user_io_interactions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    io_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    first_read_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    first_read_at: Mapped[datetime | None] = mapped_column()
    last_read_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    last_read_at: Mapped[datetime | None] = mapped_column()

    shared_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    shared_at: Mapped[datetime | None] = mapped_column()
    shared_via: Mapped[str | None] = mapped_column(Text)

    reading_time_seconds: Mapped[int | None] = mapped_column(Integer)
    scroll_depth: Mapped[float | None] = mapped_column(Float)
    bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)
    clipped_to_mindmap: Mapped[bool] = mapped_column(Boolean, default=False)

    notified_of_update: Mapped[bool] = mapped_column(Boolean, default=False)
    notified_at: Mapped[datetime | None] = mapped_column()

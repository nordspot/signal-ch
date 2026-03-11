"""Notification service — alerts users when IOs they read/shared are updated."""

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intelligence_object import IntelligenceObject
from app.models.user import User, UserIOInteraction

logger = structlog.get_logger()


async def notify_io_update(
    session: AsyncSession,
    io_id: uuid.UUID,
    new_version_number: int,
    diff_summary: dict | None = None,
):
    """Notify all users who read or shared a previous version of this IO."""
    result = await session.execute(
        select(UserIOInteraction)
        .where(UserIOInteraction.io_id == io_id)
        .where(UserIOInteraction.notified_of_update == False)  # noqa: E712
    )
    interactions = result.scalars().all()

    if not interactions:
        return

    # For now, just mark them as needing notification
    # Real implementation would send push notifications, emails, etc.
    for interaction in interactions:
        interaction.notified_of_update = True
        interaction.notified_at = datetime.now(timezone.utc)

    logger.info(
        "io_update_notifications_queued",
        io_id=str(io_id),
        version=new_version_number,
        users_notified=len(interactions),
    )


async def record_io_read(
    session: AsyncSession,
    user_id: uuid.UUID,
    io_id: uuid.UUID,
    version_id: uuid.UUID,
):
    """Record that a user read an IO version."""
    now = datetime.now(timezone.utc)

    result = await session.execute(
        select(UserIOInteraction).where(
            UserIOInteraction.user_id == user_id,
            UserIOInteraction.io_id == io_id,
        )
    )
    interaction = result.scalar_one_or_none()

    if interaction:
        interaction.last_read_version_id = version_id
        interaction.last_read_at = now
        interaction.notified_of_update = False
    else:
        interaction = UserIOInteraction(
            user_id=user_id,
            io_id=io_id,
            first_read_version_id=version_id,
            first_read_at=now,
            last_read_version_id=version_id,
            last_read_at=now,
        )
        session.add(interaction)

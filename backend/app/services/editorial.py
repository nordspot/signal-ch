"""Editorial review service."""

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intelligence_object import IOVersion, IntelligenceObject
from app.models.user import User

logger = structlog.get_logger()


async def approve_version(
    session: AsyncSession,
    version_id: uuid.UUID,
    reviewer: User,
) -> IOVersion:
    """Approve an IO version for publication."""
    result = await session.execute(select(IOVersion).where(IOVersion.id == version_id))
    version = result.scalar_one_or_none()
    if not version:
        raise ValueError("Version not found")

    version.review_status = "approved"
    version.reviewed_by = reviewer.id
    version.reviewed_at = datetime.now(timezone.utc)

    # Update IO status to published
    io_result = await session.execute(
        select(IntelligenceObject).where(IntelligenceObject.id == version.io_id)
    )
    io = io_result.scalar_one_or_none()
    if io:
        io.current_version_id = version.id
        io.status = "published"

    logger.info(
        "version_approved",
        version_id=str(version_id),
        io_id=str(version.io_id),
        reviewer=str(reviewer.id),
    )
    return version


async def reject_version(
    session: AsyncSession,
    version_id: uuid.UUID,
    reviewer: User,
    reason: str | None = None,
) -> IOVersion:
    """Reject an IO version."""
    result = await session.execute(select(IOVersion).where(IOVersion.id == version_id))
    version = result.scalar_one_or_none()
    if not version:
        raise ValueError("Version not found")

    version.review_status = "rejected"
    version.reviewed_by = reviewer.id
    version.reviewed_at = datetime.now(timezone.utc)

    logger.info(
        "version_rejected",
        version_id=str(version_id),
        io_id=str(version.io_id),
        reviewer=str(reviewer.id),
        reason=reason,
    )
    return version


async def retract_io(
    session: AsyncSession,
    io_id: uuid.UUID,
    retractor: User,
    reason: str,
) -> IntelligenceObject:
    """Retract a published IO — per Invariant #8, must be possible within 1 hour."""
    result = await session.execute(
        select(IntelligenceObject).where(IntelligenceObject.id == io_id)
    )
    io = result.scalar_one_or_none()
    if not io:
        raise ValueError("IO not found")

    io.status = "retracted"

    # Create retraction version
    retraction_version = IOVersion(
        io_id=io_id,
        version_number=(io.version_count or 0) + 1,
        trigger_type="retraction",
        review_status="approved",
        reviewed_by=retractor.id,
        reviewed_at=datetime.now(timezone.utc),
        diff_summary={"reason": reason, "retracted_by": str(retractor.id)},
    )
    session.add(retraction_version)

    io.version_count = (io.version_count or 0) + 1

    logger.info(
        "io_retracted",
        io_id=str(io_id),
        retractor=str(retractor.id),
        reason=reason,
    )
    return io

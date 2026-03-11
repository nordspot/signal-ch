import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin, require_editor
from app.database import get_db
from app.models.intelligence_object import IOVersion, IntelligenceObject
from app.models.publisher import Publisher
from app.models.source import Source
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


class ReviewAction(BaseModel):
    action: str  # approved, rejected
    notes: str | None = None


class DashboardStats(BaseModel):
    total_ios: int
    published_ios: int
    pending_reviews: int
    total_sources: int
    total_publishers: int
    total_users: int


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_editor),
):
    total_ios = (await db.execute(select(func.count(IntelligenceObject.id)))).scalar() or 0
    published = (
        await db.execute(
            select(func.count(IntelligenceObject.id)).where(IntelligenceObject.status == "published")
        )
    ).scalar() or 0
    pending = (
        await db.execute(
            select(func.count(IOVersion.id)).where(IOVersion.review_status == "pending")
        )
    ).scalar() or 0
    sources = (await db.execute(select(func.count(Source.id)))).scalar() or 0
    publishers = (await db.execute(select(func.count(Publisher.id)))).scalar() or 0
    users = (await db.execute(select(func.count(User.id)))).scalar() or 0

    return DashboardStats(
        total_ios=total_ios,
        published_ios=published,
        pending_reviews=pending,
        total_sources=sources,
        total_publishers=publishers,
        total_users=users,
    )


@router.get("/review-queue")
async def get_review_queue(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_editor),
):
    result = await db.execute(
        select(IOVersion)
        .where(IOVersion.review_status == "pending")
        .order_by(IOVersion.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    versions = result.scalars().all()

    items = []
    for v in versions:
        io_result = await db.execute(
            select(IntelligenceObject).where(IntelligenceObject.id == v.io_id)
        )
        io = io_result.scalar_one_or_none()
        items.append({
            "version_id": str(v.id),
            "io_id": str(v.io_id),
            "version_number": v.version_number,
            "trigger_type": v.trigger_type,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "content_de": v.content_de,
            "content_fr": v.content_fr,
            "content_it": v.content_it,
            "content_en": v.content_en,
            "io_category": io.category if io else None,
            "io_status": io.status if io else None,
        })

    return {"items": items, "page": page, "page_size": page_size}


@router.post("/review/{version_id}")
async def review_version(
    version_id: uuid.UUID,
    action: ReviewAction,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_editor),
):
    result = await db.execute(select(IOVersion).where(IOVersion.id == version_id))
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    version.review_status = action.action
    version.reviewed_by = user.id
    version.reviewed_at = datetime.now(timezone.utc)

    if action.action == "approved":
        io_result = await db.execute(
            select(IntelligenceObject).where(IntelligenceObject.id == version.io_id)
        )
        io = io_result.scalar_one_or_none()
        if io:
            io.current_version_id = version.id
            io.status = "published"

    return {"status": "ok", "review_status": action.action}

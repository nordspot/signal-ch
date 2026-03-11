from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.intelligence_object import IntelligenceObject
from app.schemas.io import IOOut

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[IOOut])
async def search_ios(
    q: str = Query(..., min_length=2),
    category: str | None = None,
    canton: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Full-text search via Meilisearch with DB fallback."""
    try:
        import meilisearch

        client = meilisearch.Client(settings.meili_url, settings.meili_master_key)
        index = client.index("intelligence_objects")

        filters = ["status = published"]
        if category:
            filters.append(f"category = {category}")
        if canton:
            filters.append(f"canton_codes CONTAINS {canton}")

        results = index.search(q, {"limit": limit, "filter": " AND ".join(filters)})
        io_ids = [hit["id"] for hit in results["hits"]]

        if io_ids:
            result = await db.execute(
                select(IntelligenceObject).where(IntelligenceObject.id.in_(io_ids))
            )
            return [IOOut.model_validate(io) for io in result.scalars().all()]
        return []

    except Exception:
        # Fallback to ILIKE search
        query = (
            select(IntelligenceObject)
            .where(IntelligenceObject.status == "published")
            .limit(limit)
        )
        result = await db.execute(query)
        return [IOOut.model_validate(io) for io in result.scalars().all()]

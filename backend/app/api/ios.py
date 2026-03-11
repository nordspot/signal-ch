import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_optional_user
from app.database import get_db
from app.models.intelligence_object import IOEntity, IOSource, IOVersion, IntelligenceObject
from app.models.source import Source
from app.models.user import User
from app.schemas.io import IOFilters, IOListOut, IOOut, IOVersionOut
from app.schemas.source import SourceOut

router = APIRouter(prefix="/ios", tags=["intelligence_objects"])


@router.get("", response_model=IOListOut)
async def list_ios(
    category: str | None = None,
    scope: str | None = None,
    canton: str | None = None,
    status: str = "published",
    language: str = "de",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    query = select(IntelligenceObject).where(IntelligenceObject.status == status)

    if category:
        query = query.where(IntelligenceObject.category == category)
    if scope:
        query = query.where(IntelligenceObject.scope == scope)
    if canton:
        query = query.where(IntelligenceObject.canton_codes.contains([canton]))

    # Count total
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginate
    query = query.order_by(IntelligenceObject.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    ios = result.scalars().all()

    # Attach current versions
    items = []
    for io in ios:
        io_out = IOOut.model_validate(io)
        if io.current_version_id:
            ver_result = await db.execute(
                select(IOVersion).where(IOVersion.id == io.current_version_id)
            )
            version = ver_result.scalar_one_or_none()
            if version:
                io_out.current_version = IOVersionOut.model_validate(version)
        items.append(io_out)

    return IOListOut(items=items, total=total, page=page, page_size=page_size)


@router.get("/{io_id}", response_model=IOOut)
async def get_io(io_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IntelligenceObject).where(IntelligenceObject.id == io_id)
    )
    io = result.scalar_one_or_none()
    if not io:
        raise HTTPException(status_code=404, detail="Intelligence Object not found")

    io_out = IOOut.model_validate(io)
    if io.current_version_id:
        ver_result = await db.execute(
            select(IOVersion).where(IOVersion.id == io.current_version_id)
        )
        version = ver_result.scalar_one_or_none()
        if version:
            io_out.current_version = IOVersionOut.model_validate(version)

    return io_out


@router.get("/{io_id}/versions", response_model=list[IOVersionOut])
async def get_io_versions(io_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IOVersion)
        .where(IOVersion.io_id == io_id)
        .order_by(IOVersion.version_number.desc())
    )
    return [IOVersionOut.model_validate(v) for v in result.scalars().all()]


@router.get("/{io_id}/sources", response_model=list[SourceOut])
async def get_io_sources(io_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Source, IOSource.contribution_type)
        .join(IOSource, IOSource.source_id == Source.id)
        .where(IOSource.io_id == io_id)
        .order_by(Source.original_published_at.desc())
    )
    sources = []
    for row in result.all():
        source, contribution_type = row
        out = SourceOut.model_validate(source)
        out.contribution_type = contribution_type
        sources.append(out)
    return sources

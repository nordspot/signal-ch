import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.entity import Entity, EntityRelation
from app.models.intelligence_object import IOEntity, IntelligenceObject
from app.schemas.entity import EntityListOut, EntityOut, EntityRelationOut
from app.schemas.io import IOOut

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("", response_model=EntityListOut)
async def list_entities(
    entity_type: str | None = None,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Entity)
    if entity_type:
        query = query.where(Entity.entity_type == entity_type)
    if q:
        query = query.where(Entity.canonical_name.ilike(f"%{q}%"))

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Entity.mention_count.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = [EntityOut.model_validate(e) for e in result.scalars().all()]

    return EntityListOut(items=items, total=total)


@router.get("/{entity_id}", response_model=EntityOut)
async def get_entity(entity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Entity).where(Entity.id == entity_id))
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return EntityOut.model_validate(entity)


@router.get("/{entity_id}/ios", response_model=list[IOOut])
async def get_entity_ios(entity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IntelligenceObject)
        .join(IOEntity, IOEntity.io_id == IntelligenceObject.id)
        .where(IOEntity.entity_id == entity_id)
        .where(IntelligenceObject.status == "published")
        .order_by(IntelligenceObject.created_at.desc())
        .limit(50)
    )
    return [IOOut.model_validate(io) for io in result.scalars().all()]


@router.get("/{entity_id}/relations", response_model=list[EntityRelationOut])
async def get_entity_relations(entity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EntityRelation).where(
            (EntityRelation.source_entity_id == entity_id)
            | (EntityRelation.target_entity_id == entity_id)
        )
    )
    return [EntityRelationOut.model_validate(r) for r in result.scalars().all()]

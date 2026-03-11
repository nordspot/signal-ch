import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.democracy import VoteAndInitiative

router = APIRouter(prefix="/votes", tags=["democracy"])


class VoteOut:
    pass  # inline below


from pydantic import BaseModel
from datetime import date


class VoteOut(BaseModel):
    id: uuid.UUID
    vote_type: str
    level: str
    canton: str | None = None
    title_de: str | None = None
    title_fr: str | None = None
    title_it: str | None = None
    official_url: str | None = None
    vote_date: date | None = None
    status: str
    result: dict | None = None
    pro_arguments: dict | None = None
    contra_arguments: dict | None = None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[VoteOut])
async def list_votes(
    status: str | None = None,
    level: str | None = None,
    canton: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(VoteAndInitiative)
    if status:
        query = query.where(VoteAndInitiative.status == status)
    if level:
        query = query.where(VoteAndInitiative.level == level)
    if canton:
        query = query.where(VoteAndInitiative.canton == canton)
    query = query.order_by(VoteAndInitiative.vote_date.desc()).limit(limit)
    result = await db.execute(query)
    return [VoteOut.model_validate(v) for v in result.scalars().all()]


@router.get("/{vote_id}", response_model=VoteOut)
async def get_vote(vote_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(VoteAndInitiative).where(VoteAndInitiative.id == vote_id)
    )
    vote = result.scalar_one_or_none()
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    return VoteOut.model_validate(vote)

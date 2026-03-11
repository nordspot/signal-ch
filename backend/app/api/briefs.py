from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_optional_user
from app.database import get_db
from app.models.user import User
from app.services.brief_generator import generate_daily_brief

router = APIRouter(prefix="/briefs", tags=["briefs"])


@router.get("/daily")
async def get_daily_brief(
    language: str = Query(default="de"),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    return await generate_daily_brief(db, user=user, language=language)

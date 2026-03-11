"""Daily brief generator — creates personalized morning/evening briefs."""

import json
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.intelligence_object import IOVersion, IntelligenceObject
from app.models.user import User
from app.synthesis.prompts import BRIEF_SYSTEM_PROMPT, BRIEF_USER_PROMPT

logger = structlog.get_logger()


async def generate_daily_brief(
    session: AsyncSession,
    user: User | None = None,
    language: str = "de",
    max_stories: int = 5,
) -> dict:
    """Generate a daily brief from today's top published IOs."""
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    query = (
        select(IntelligenceObject)
        .where(IntelligenceObject.status == "published")
        .where(IntelligenceObject.updated_at >= since)
        .order_by(
            IntelligenceObject.confirmation_density.desc().nullslast(),
            IntelligenceObject.created_at.desc(),
        )
        .limit(max_stories * 2)
    )

    # Apply user preferences if available
    if user and user.interests:
        # Boost matching categories but still include others
        pass  # Future: weighted ranking

    result = await session.execute(query)
    ios = result.scalars().all()

    if not ios:
        return {
            "greeting": _greeting(language),
            "date": datetime.now(timezone.utc).strftime("%d.%m.%Y"),
            "top_stories": [],
            "developing": [],
            "watch_today": "",
            "closing": "",
        }

    # Build stories list
    stories = []
    for io in ios[:max_stories]:
        story = {"io_id": str(io.id), "category": io.category}

        if io.current_version_id:
            ver_result = await session.execute(
                select(IOVersion).where(IOVersion.id == io.current_version_id)
            )
            version = ver_result.scalar_one_or_none()
            if version:
                content = getattr(version, f"content_{language}", None)
                if content and isinstance(content, dict):
                    story["title"] = content.get("title", "")
                    story["summary"] = content.get("summary", "")

        stories.append(story)

    # Try Claude API for polished brief
    if settings.anthropic_api_key:
        return await _claude_brief(stories, language)

    # Fallback: structured brief without Claude
    return {
        "greeting": _greeting(language),
        "date": datetime.now(timezone.utc).strftime("%d.%m.%Y"),
        "top_stories": stories,
        "developing": [],
        "watch_today": "",
        "closing": _closing(language),
    }


async def _claude_brief(stories: list[dict], language: str) -> dict:
    """Generate polished brief via Claude API."""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        stories_text = "\n\n".join(
            f"Story {i + 1} ({s.get('category', 'general')}):\n"
            f"Title: {s.get('title', 'N/A')}\n"
            f"Summary: {s.get('summary', 'N/A')}\n"
            f"IO ID: {s.get('io_id', '')}"
            for i, s in enumerate(stories)
        )

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=BRIEF_SYSTEM_PROMPT.format(language=language),
            messages=[{"role": "user", "content": BRIEF_USER_PROMPT.format(stories=stories_text)}],
        )

        response_text = message.content[0].text
        try:
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    except Exception as e:
        logger.error("brief_claude_error", error=str(e))

    # Fallback
    return {
        "greeting": _greeting(language),
        "date": datetime.now(timezone.utc).strftime("%d.%m.%Y"),
        "top_stories": stories,
        "developing": [],
        "watch_today": "",
        "closing": _closing(language),
    }


def _greeting(lang: str) -> str:
    greetings = {
        "de": "Guten Morgen. Hier ist Ihr Signal-Briefing.",
        "fr": "Bonjour. Voici votre briefing Signal.",
        "it": "Buongiorno. Ecco il vostro briefing Signal.",
        "en": "Good morning. Here's your Signal briefing.",
    }
    return greetings.get(lang, greetings["de"])


def _closing(lang: str) -> str:
    closings = {
        "de": "Bleiben Sie informiert. Signal.ch",
        "fr": "Restez informé. Signal.ch",
        "it": "Rimanete informati. Signal.ch",
        "en": "Stay informed. Signal.ch",
    }
    return closings.get(lang, closings["de"])

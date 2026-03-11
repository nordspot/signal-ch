"""Base ingestion connector — all connectors inherit from this."""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publisher import Publisher
from app.models.source import Source

logger = structlog.get_logger()


class BaseConnector(ABC):
    """Base class for all ingestion connectors."""

    publisher_slug: str  # must be set by subclass

    def __init__(self, session: AsyncSession):
        self.session = session
        self.http = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "Signal.ch/0.1 (https://signal.ch; news-intelligence)"},
            follow_redirects=True,
        )
        self._publisher: Publisher | None = None

    async def get_publisher(self) -> Publisher:
        if self._publisher is None:
            result = await self.session.execute(
                select(Publisher).where(Publisher.slug == self.publisher_slug)
            )
            self._publisher = result.scalar_one_or_none()
            if not self._publisher:
                raise RuntimeError(f"Publisher '{self.publisher_slug}' not found. Run seed first.")
        return self._publisher

    async def url_exists(self, url: str) -> bool:
        """Dedup check: has this URL already been ingested?"""
        result = await self.session.execute(
            select(Source.id).where(Source.original_url == url).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def create_source(
        self,
        url: str,
        title: str | None,
        language: str | None,
        published_at: datetime | None,
        snippet: str | None = None,
        full_text: str | None = None,
        author: str | None = None,
    ) -> Source:
        """Create a source record with proper legal flags from publisher config."""
        publisher = await self.get_publisher()

        source = Source(
            source_type="government" if publisher.license_type == "public_domain" else "rss_metadata",
            license_status=publisher.license_type or "unlicensed",
            can_display_full_text=publisher.license_allows_full_text,
            can_synthesize_from=publisher.license_allows_synthesis,
            requires_link_back=True,
            original_url=url,
            original_title=title,
            original_language=language,
            original_published_at=published_at or datetime.now(timezone.utc),
            snippet=snippet,
            full_text_encrypted=full_text if publisher.license_allows_full_text else None,
            publisher_id=publisher.id,
            attribution_text=f"Source: {publisher.name}",
            author_name=author,
            publisher_reliability_score=publisher.reliability_score,
        )
        self.session.add(source)
        await self.session.flush()

        logger.info(
            "source_created",
            url=url,
            publisher=self.publisher_slug,
            source_id=str(source.id),
        )
        return source

    @abstractmethod
    async def fetch(self) -> list[Source]:
        """Fetch new content from this source. Returns list of created Source records."""
        ...

    async def close(self):
        await self.http.aclose()

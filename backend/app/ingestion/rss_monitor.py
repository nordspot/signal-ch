"""Generic RSS feed monitor — processes all publishers with configured RSS feeds."""

from datetime import datetime, timezone

import feedparser
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publisher import Publisher
from app.models.source import Source

logger = structlog.get_logger()


class RssMonitor:
    """Monitors all RSS feeds from all publishers in the database."""

    def __init__(self, session: AsyncSession):
        self.session = session
        import httpx

        self.http = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "Signal.ch/0.1 (https://signal.ch; news-intelligence)"},
            follow_redirects=True,
        )

    async def fetch_all(self) -> list[Source]:
        """Fetch new items from all publisher RSS feeds."""
        sources = []

        result = await self.session.execute(
            select(Publisher).where(
                Publisher.rss_feeds != "[]",
                Publisher.rss_feeds.isnot(None),
            )
        )
        publishers = result.scalars().all()

        for publisher in publishers:
            feeds = publisher.rss_feeds or []
            for feed_config in feeds:
                if not isinstance(feed_config, dict) or not feed_config.get("url"):
                    continue

                try:
                    new_sources = await self._fetch_feed(publisher, feed_config)
                    sources.extend(new_sources)
                except Exception as e:
                    logger.error(
                        "rss_feed_error",
                        publisher=publisher.slug,
                        feed_url=feed_config.get("url"),
                        error=str(e),
                    )

        logger.info("rss_monitor_complete", total_new=len(sources))
        return sources

    async def _fetch_feed(self, publisher: Publisher, feed_config: dict) -> list[Source]:
        """Fetch a single RSS feed and create source records."""
        sources = []
        url = feed_config["url"]

        response = await self.http.get(url)
        response.raise_for_status()
        feed = feedparser.parse(response.text)

        for entry in feed.entries:
            entry_url = entry.get("link", "")
            if not entry_url:
                continue

            # Dedup
            existing = await self.session.execute(
                select(Source.id).where(Source.original_url == entry_url).limit(1)
            )
            if existing.scalar_one_or_none():
                continue

            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            snippet = entry.get("summary", "")
            if len(snippet) > 500:
                snippet = snippet[:497] + "..."

            # Determine source type and legal flags from publisher config
            is_government = publisher.license_type == "public_domain"

            source = Source(
                source_type="government" if is_government else "rss_metadata",
                license_status=publisher.license_type or "rss_metadata_only",
                can_display_full_text=publisher.license_allows_full_text,
                can_synthesize_from=publisher.license_allows_synthesis,
                requires_link_back=True,
                original_url=entry_url,
                original_title=entry.get("title"),
                original_language=feed_config.get("language", "de"),
                original_published_at=published or datetime.now(timezone.utc),
                snippet=snippet,
                full_text_encrypted=entry.get("summary") if publisher.license_allows_full_text else None,
                publisher_id=publisher.id,
                attribution_text=f"Source: {publisher.name}",
                author_name=entry.get("author"),
                publisher_reliability_score=publisher.reliability_score,
            )
            self.session.add(source)
            sources.append(source)

        if sources:
            await self.session.flush()
            logger.info(
                "rss_feed_fetched",
                publisher=publisher.slug,
                feed=url,
                new_items=len(sources),
            )

        return sources

    async def close(self):
        await self.http.aclose()

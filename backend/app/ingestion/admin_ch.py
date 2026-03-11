"""Connector for admin.ch — Swiss Federal Council press releases via RSS."""

from datetime import datetime, timezone

import feedparser
import structlog

from app.ingestion.base import BaseConnector
from app.models.source import Source

logger = structlog.get_logger()

ADMIN_CH_FEEDS = [
    {"url": "https://www.admin.ch/gov/de/start.html.rss", "language": "de"},
    {"url": "https://www.admin.ch/gov/fr/accueil.html.rss", "language": "fr"},
    {"url": "https://www.admin.ch/gov/it/pagina-iniziale.html.rss", "language": "it"},
]


class AdminChConnector(BaseConnector):
    publisher_slug = "admin-ch"

    async def fetch(self) -> list[Source]:
        sources = []
        for feed_config in ADMIN_CH_FEEDS:
            try:
                response = await self.http.get(feed_config["url"])
                response.raise_for_status()
                feed = feedparser.parse(response.text)

                for entry in feed.entries:
                    url = entry.get("link", "")
                    if not url or await self.url_exists(url):
                        continue

                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

                    snippet = entry.get("summary", "")
                    if len(snippet) > 500:
                        snippet = snippet[:497] + "..."

                    source = await self.create_source(
                        url=url,
                        title=entry.get("title"),
                        language=feed_config["language"],
                        published_at=published,
                        snippet=snippet,
                        full_text=entry.get("summary"),
                    )
                    sources.append(source)

                logger.info(
                    "admin_ch_fetched",
                    language=feed_config["language"],
                    entries=len(feed.entries),
                    new=len(sources),
                )

            except Exception as e:
                logger.error("admin_ch_fetch_error", language=feed_config["language"], error=str(e))

        return sources

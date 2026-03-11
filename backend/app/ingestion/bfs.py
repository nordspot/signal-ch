"""Connector for BFS (Federal Statistical Office) — statistics and datasets."""

from datetime import datetime, timezone

import structlog

from app.ingestion.base import BaseConnector
from app.models.source import Source

logger = structlog.get_logger()

BFS_NEWS_URL = "https://www.bfs.admin.ch/bfs/de/home/aktuell.html"


class BfsConnector(BaseConnector):
    publisher_slug = "bfs"

    async def fetch(self) -> list[Source]:
        sources = []

        # BFS publishes via opendata.swiss as well, but also has its own news feed
        await self._fetch_news(sources)
        await self._fetch_datasets(sources)

        return sources

    async def _fetch_news(self, sources: list[Source]):
        """Fetch BFS news/press releases."""
        try:
            # BFS RSS feed for new publications
            rss_urls = [
                ("https://www.bfs.admin.ch/bfs/de/home/aktuell/neue-veroeffentlichungen.assetdetail.rss", "de"),
                ("https://www.bfs.admin.ch/bfs/fr/home/actualites/nouvelles-publications.assetdetail.rss", "fr"),
            ]

            for rss_url, lang in rss_urls:
                try:
                    import feedparser

                    response = await self.http.get(rss_url)
                    if response.status_code != 200:
                        continue

                    feed = feedparser.parse(response.text)

                    for entry in feed.entries[:20]:
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
                            language=lang,
                            published_at=published,
                            snippet=snippet,
                            full_text=entry.get("summary"),
                        )
                        sources.append(source)

                    logger.info("bfs_news_fetched", language=lang, count=len(sources))

                except Exception as e:
                    logger.error("bfs_news_feed_error", language=lang, error=str(e))

        except Exception as e:
            logger.error("bfs_news_error", error=str(e))

    async def _fetch_datasets(self, sources: list[Source]):
        """Fetch recently updated BFS datasets from opendata.swiss."""
        try:
            response = await self.http.get(
                "https://ckan.opendata.swiss/api/3/action/package_search",
                params={
                    "fq": "organization:bundesamt-fur-statistik-bfs",
                    "sort": "metadata_modified desc",
                    "rows": 20,
                },
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                return

            for dataset in data["result"]["results"]:
                url = f"https://opendata.swiss/dataset/{dataset['name']}"
                if await self.url_exists(url):
                    continue

                title = dataset.get("title", {})
                title_text = title.get("de") or title.get("fr") or dataset.get("name", "")

                description = dataset.get("description", {})
                snippet_text = description.get("de") or description.get("fr") or ""
                if len(snippet_text) > 500:
                    snippet_text = snippet_text[:497] + "..."

                modified = dataset.get("metadata_modified")
                published_at = None
                if modified:
                    try:
                        published_at = datetime.fromisoformat(modified.replace("Z", "+00:00"))
                    except ValueError:
                        pass

                source = await self.create_source(
                    url=url,
                    title=title_text,
                    language="de",
                    published_at=published_at,
                    snippet=snippet_text,
                )
                sources.append(source)

            logger.info("bfs_datasets_fetched", count=len(sources))

        except Exception as e:
            logger.error("bfs_datasets_error", error=str(e))

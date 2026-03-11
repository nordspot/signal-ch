"""Connector for opendata.swiss — CKAN API with 14,279+ datasets."""

from datetime import datetime, timezone

import structlog

from app.ingestion.base import BaseConnector
from app.models.source import Source

logger = structlog.get_logger()

CKAN_BASE = "https://ckan.opendata.swiss/api/3/action/"


class OpenDataSwissConnector(BaseConnector):
    publisher_slug = "opendata-swiss"

    async def fetch(self) -> list[Source]:
        sources = []

        try:
            # Fetch recently modified datasets
            response = await self.http.get(
                f"{CKAN_BASE}package_search",
                params={
                    "sort": "metadata_modified desc",
                    "rows": 50,
                    "q": "*:*",
                },
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                logger.error("opendata_swiss_api_error", response=data)
                return sources

            for dataset in data["result"]["results"]:
                url = f"https://opendata.swiss/dataset/{dataset['name']}"
                if await self.url_exists(url):
                    continue

                modified = dataset.get("metadata_modified")
                published_at = None
                if modified:
                    try:
                        published_at = datetime.fromisoformat(modified.replace("Z", "+00:00"))
                    except ValueError:
                        published_at = datetime.now(timezone.utc)

                # Build snippet from description
                description = dataset.get("description", {})
                snippet_text = (
                    description.get("de")
                    or description.get("fr")
                    or description.get("it")
                    or description.get("en")
                    or ""
                )
                if len(snippet_text) > 500:
                    snippet_text = snippet_text[:497] + "..."

                title = dataset.get("title", {})
                title_text = (
                    title.get("de")
                    or title.get("fr")
                    or title.get("it")
                    or title.get("en")
                    or dataset.get("name", "")
                )

                # Determine language from available titles
                lang = "de"
                if title.get("fr") and not title.get("de"):
                    lang = "fr"
                elif title.get("it") and not title.get("de"):
                    lang = "it"

                source = await self.create_source(
                    url=url,
                    title=title_text,
                    language=lang,
                    published_at=published_at,
                    snippet=snippet_text,
                )
                sources.append(source)

            logger.info(
                "opendata_swiss_fetched",
                total_datasets=data["result"]["count"],
                new_sources=len(sources),
            )

        except Exception as e:
            logger.error("opendata_swiss_error", error=str(e))

        return sources

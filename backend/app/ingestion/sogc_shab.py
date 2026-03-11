"""Connector for SOGC/SHAB — Swiss Official Gazette of Commerce.

Gold mine for business news: company registrations, bankruptcies,
board changes, capital modifications.
"""

from datetime import datetime, timezone

import structlog
from bs4 import BeautifulSoup

from app.ingestion.base import BaseConnector
from app.models.source import Source

logger = structlog.get_logger()

SHAB_SEARCH_URL = "https://www.shab.ch/#!/search/publications"
SHAB_API_URL = "https://www.shab.ch/api/v1/publications"


class SogcShabConnector(BaseConnector):
    publisher_slug = "sogc-shab"

    async def fetch(self) -> list[Source]:
        sources = []

        try:
            # SHAB has a REST API for publication search
            response = await self.http.get(
                SHAB_API_URL,
                params={
                    "publicationStates": "PUBLISHED",
                    "pageRequest.page": 0,
                    "pageRequest.size": 50,
                },
            )

            if response.status_code == 200:
                data = response.json()
                publications = data if isinstance(data, list) else data.get("content", [])

                for pub in publications:
                    pub_id = pub.get("id", "")
                    url = f"https://www.shab.ch/#!/search/publications/detail/{pub_id}"

                    if await self.url_exists(url):
                        continue

                    pub_date = None
                    date_str = pub.get("publicationDate") or pub.get("registrationDate")
                    if date_str:
                        try:
                            pub_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        except ValueError:
                            pub_date = datetime.now(timezone.utc)

                    # Extract key info
                    title = pub.get("title") or pub.get("rubric", "SOGC Publication")
                    snippet_parts = []
                    if pub.get("rubric"):
                        snippet_parts.append(f"Category: {pub['rubric']}")
                    if pub.get("subRubric"):
                        snippet_parts.append(f"Type: {pub['subRubric']}")
                    if pub.get("companyName"):
                        snippet_parts.append(f"Company: {pub['companyName']}")
                    if pub.get("companyUid"):
                        snippet_parts.append(f"UID: {pub['companyUid']}")
                    if pub.get("cantons"):
                        snippet_parts.append(f"Canton: {', '.join(pub['cantons'])}")

                    source = await self.create_source(
                        url=url,
                        title=title,
                        language="de",
                        published_at=pub_date,
                        snippet=" | ".join(snippet_parts) if snippet_parts else title,
                        full_text=pub.get("message") or pub.get("text"),
                    )
                    sources.append(source)

                logger.info("sogc_shab_fetched", new_sources=len(sources))

            else:
                # Fallback: scrape the HTML search page
                await self._scrape_fallback(sources)

        except Exception as e:
            logger.error("sogc_shab_error", error=str(e))
            await self._scrape_fallback(sources)

        return sources

    async def _scrape_fallback(self, sources: list[Source]):
        """Fallback scraper if API is unavailable."""
        try:
            response = await self.http.get("https://www.shab.ch/")
            if response.status_code == 200:
                logger.info("sogc_shab_fallback_accessed")
        except Exception as e:
            logger.error("sogc_shab_fallback_error", error=str(e))

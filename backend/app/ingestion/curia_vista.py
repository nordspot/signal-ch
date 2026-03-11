"""Connector for Curia Vista / Swiss Parliament OData API."""

from datetime import datetime, timezone

import structlog

from app.ingestion.base import BaseConnector
from app.models.source import Source

logger = structlog.get_logger()

ODATA_BASE = "https://ws.parlament.ch/odata.svc/"


class CuriaVistaConnector(BaseConnector):
    publisher_slug = "curia-vista"

    async def fetch(self) -> list[Source]:
        sources = []

        # Fetch recent business items (Geschaefte)
        await self._fetch_businesses(sources)
        # Fetch recent votes
        await self._fetch_votes(sources)
        # Fetch recent press releases
        await self._fetch_press_releases(sources)

        return sources

    async def _fetch_businesses(self, sources: list[Source]):
        """Fetch recent parliamentary business items."""
        try:
            response = await self.http.get(
                f"{ODATA_BASE}Business",
                params={
                    "$format": "json",
                    "$orderby": "SubmissionDate desc",
                    "$top": 30,
                    "$select": "ID,BusinessShortNumber,Title,SubmissionDate,BusinessTypeName,Language",
                },
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("d", {}).get("results", data.get("d", [])):
                if isinstance(item, dict):
                    biz_id = item.get("ID") or item.get("BusinessShortNumber", "")
                    url = f"https://www.parlament.ch/de/ratsbetrieb/suche-curia-vista/geschaeft?AffairId={biz_id}"

                    if await self.url_exists(url):
                        continue

                    submission_date = None
                    date_str = item.get("SubmissionDate", "")
                    if date_str and "/Date(" in date_str:
                        try:
                            ts = int(date_str.split("(")[1].split(")")[0].split("+")[0].split("-")[0])
                            submission_date = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                        except (ValueError, IndexError):
                            pass

                    source = await self.create_source(
                        url=url,
                        title=item.get("Title", ""),
                        language=item.get("Language", "de").lower()[:2],
                        published_at=submission_date,
                        snippet=f"{item.get('BusinessTypeName', '')}: {item.get('Title', '')}",
                    )
                    sources.append(source)

            logger.info("curia_vista_businesses_fetched", count=len(sources))

        except Exception as e:
            logger.error("curia_vista_businesses_error", error=str(e))

    async def _fetch_votes(self, sources: list[Source]):
        """Fetch recent National/States Council votes."""
        try:
            response = await self.http.get(
                f"{ODATA_BASE}Voting",
                params={
                    "$format": "json",
                    "$orderby": "Date desc",
                    "$top": 20,
                    "$select": "ID,Date,Subject,MeaningYes,MeaningNo,Language",
                },
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("d", {}).get("results", data.get("d", [])):
                if isinstance(item, dict):
                    vote_id = item.get("ID", "")
                    url = f"https://www.parlament.ch/de/ratsbetrieb/abstimmungen/abstimmung?VoteId={vote_id}"

                    if await self.url_exists(url):
                        continue

                    source = await self.create_source(
                        url=url,
                        title=item.get("Subject", ""),
                        language="de",
                        published_at=None,
                        snippet=f"Vote: {item.get('Subject', '')} — Yes: {item.get('MeaningYes', '')}, No: {item.get('MeaningNo', '')}",
                    )
                    sources.append(source)

        except Exception as e:
            logger.error("curia_vista_votes_error", error=str(e))

    async def _fetch_press_releases(self, sources: list[Source]):
        """Fetch parliament press releases."""
        try:
            response = await self.http.get(
                f"{ODATA_BASE}MemberCouncilHistory",
                params={
                    "$format": "json",
                    "$top": 10,
                    "$orderby": "DateJoining desc",
                },
            )
            # This is a placeholder — real implementation would use the press release endpoint
            response.raise_for_status()

        except Exception as e:
            logger.error("curia_vista_press_error", error=str(e))

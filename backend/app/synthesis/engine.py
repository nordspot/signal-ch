"""Synthesis engine — generates IO content from sources using Claude API."""

import json
import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.intelligence_object import IOSource, IOVersion, IntelligenceObject
from app.models.source import Source
from app.synthesis.prompts import SYNTHESIS_SYSTEM_PROMPT, SYNTHESIS_USER_PROMPT

logger = structlog.get_logger()


class SynthesisEngine:
    """Generates synthesized IO content from contributing sources."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def synthesize_io(
        self,
        io_id: uuid.UUID,
        language: str = "de",
        trigger_type: str = "initial",
        trigger_source_ids: list[uuid.UUID] | None = None,
    ) -> IOVersion | None:
        """Generate a new synthesis version for an IO."""

        # 1. Gather all sources for this IO
        result = await self.session.execute(
            select(Source, IOSource.contribution_type)
            .join(IOSource, IOSource.source_id == Source.id)
            .where(IOSource.io_id == io_id)
            .where(Source.can_synthesize_from == True)  # noqa: E712
            .order_by(Source.original_published_at.desc())
        )
        source_rows = result.all()

        if not source_rows:
            logger.warning("synthesis_no_sources", io_id=str(io_id))
            return None

        # 2. Extract facts from sources
        extracted_facts = []
        attributed_quotes = []
        contradictions = []

        for source, contribution_type in source_rows:
            fact_text = source.snippet or source.original_title or ""
            attribution = source.attribution_text

            if contribution_type == "contradicts":
                contradictions.append(f"[{attribution}]: {fact_text}")
            else:
                extracted_facts.append(f"[{attribution}]: {fact_text}")

        # 3. Call Claude API for synthesis
        content = await self._call_claude(
            language=language,
            source_count=len(source_rows),
            extracted_facts="\n".join(extracted_facts) or "No confirmed facts available yet.",
            attributed_quotes="\n".join(attributed_quotes) or "No attributed statements.",
            contradictions="\n".join(contradictions) or "No contradictions detected.",
            entity_context="(Knowledge graph context not yet available)",
        )

        if not content:
            return None

        # 4. Create new version
        io_result = await self.session.execute(
            select(IntelligenceObject).where(IntelligenceObject.id == io_id)
        )
        io = io_result.scalar_one_or_none()
        if not io:
            return None

        version_number = (io.version_count or 0) + 1

        version = IOVersion(
            io_id=io_id,
            version_number=version_number,
            trigger_type=trigger_type,
            trigger_source_ids=trigger_source_ids or [],
            review_status="pending",
            **{f"content_{language}": content},
        )
        self.session.add(version)
        await self.session.flush()

        # Update IO
        io.current_version_id = version.id
        io.version_count = version_number
        io.status = "review"

        # Update quality indicators from synthesis
        quality = content.get("quality_assessment", {})
        if quality:
            io.confirmation_density = quality.get("confirmation_density")
            io.completeness_score = quality.get("completeness_score")
            missing = quality.get("missing_elements", [])
            if missing:
                io.missing_elements = missing

        logger.info(
            "synthesis_complete",
            io_id=str(io_id),
            version=version_number,
            language=language,
        )
        return version

    async def _call_claude(
        self,
        language: str,
        source_count: int,
        extracted_facts: str,
        attributed_quotes: str,
        contradictions: str,
        entity_context: str,
    ) -> dict | None:
        """Call Claude API for synthesis."""
        if not settings.anthropic_api_key:
            logger.warning("synthesis_no_api_key")
            return self._fallback_synthesis(extracted_facts, language)

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

            system_prompt = SYNTHESIS_SYSTEM_PROMPT.format(language=language)
            user_prompt = SYNTHESIS_USER_PROMPT.format(
                source_count=source_count,
                extracted_facts=extracted_facts,
                attributed_quotes=attributed_quotes,
                contradictions=contradictions,
                entity_context=entity_context,
            )

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            response_text = message.content[0].text

            # Parse JSON from response
            try:
                # Try to extract JSON from response
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response_text.strip()

                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error("synthesis_json_parse_error", response=response_text[:200])
                return self._fallback_synthesis(extracted_facts, language)

        except Exception as e:
            logger.error("claude_api_error", error=str(e))
            return self._fallback_synthesis(extracted_facts, language)

    def _fallback_synthesis(self, facts: str, language: str) -> dict:
        """Fallback synthesis when Claude API is unavailable."""
        lines = facts.strip().split("\n")
        title = lines[0] if lines else "Developing Story"
        # Clean up title
        if title.startswith("["):
            title = title.split("]: ", 1)[-1] if "]: " in title else title

        return {
            "title": title[:200],
            "lead": facts[:300] if facts else "",
            "sections": [
                {
                    "type": "factual_core",
                    "content": facts,
                    "attributions": [],
                }
            ],
            "summary": facts[:200] if facts else "",
            "quality_assessment": {
                "confirmation_density": 0.3,
                "completeness_score": 0.2,
                "missing_elements": ["Full synthesis pending — API key required"],
            },
        }

"""Source processing pipeline — NER, classification, clustering, IO assignment."""

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import Entity
from app.models.intelligence_object import IOEntity, IOSource, IOVersion, IntelligenceObject
from app.models.source import Source
from app.nlp.classification import classify_category, detect_cantons, detect_language, detect_scope
from app.nlp.embeddings import compute_similarity, generate_embedding
from app.nlp.entity_resolution import EntityResolver
from app.nlp.ner import extract_entities

logger = structlog.get_logger()

CLUSTERING_THRESHOLD = 0.85


class ProcessingPipeline:
    """Processes unprocessed sources through the full NLP pipeline."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.resolver = EntityResolver(session)

    async def process_batch(self, batch_size: int = 20) -> int:
        """Process a batch of unprocessed sources."""
        result = await self.session.execute(
            select(Source)
            .where(Source.processed == False)  # noqa: E712
            .order_by(Source.created_at.asc())
            .limit(batch_size)
        )
        sources = result.scalars().all()

        count = 0
        for source in sources:
            try:
                await self._process_source(source)
                source.processed = True
                count += 1
            except Exception as e:
                logger.error("source_processing_error", source_id=str(source.id), error=str(e))

        if count:
            await self.session.flush()
            logger.info("pipeline_batch_complete", processed=count, total=len(sources))

        return count

    async def _process_source(self, source: Source):
        """Full processing pipeline for a single source."""
        text = source.original_title or ""
        if source.snippet:
            text += " " + source.snippet
        if source.full_text_encrypted and source.can_display_full_text:
            text += " " + source.full_text_encrypted

        if not text.strip():
            return

        # 1. Classify
        if not source.original_language:
            source.original_language = detect_language(text)

        # 2. NER
        entities = extract_entities(text)
        source.extracted_entities = [e.to_dict() for e in entities]

        # 3. Resolve entities to canonical records
        resolved_entities: list[Entity] = []
        for mention in entities:
            entity = await self.resolver.resolve(mention)
            entity.mention_count = (entity.mention_count or 0) + 1
            entity.last_mentioned_at = datetime.now(timezone.utc)
            resolved_entities.append(entity)

        # 4. Generate embedding
        embedding = await generate_embedding(text)
        if embedding:
            source.embedding = embedding

        # 5. Cluster — find matching IO or create new one
        io = await self._find_or_create_io(source, text, embedding, resolved_entities)

        # 6. Link source to IO
        source.assigned_io_id = io.id

        # Add IO-Source mapping
        existing_link = await self.session.execute(
            select(IOSource).where(IOSource.io_id == io.id, IOSource.source_id == source.id)
        )
        if not existing_link.scalar_one_or_none():
            io_source = IOSource(
                io_id=io.id,
                source_id=source.id,
                contribution_type="primary_source" if io.version_count == 0 else "adds_detail",
            )
            self.session.add(io_source)

        # Add IO-Entity mappings
        for entity in resolved_entities:
            existing_ie = await self.session.execute(
                select(IOEntity).where(IOEntity.io_id == io.id, IOEntity.entity_id == entity.id)
            )
            if not existing_ie.scalar_one_or_none():
                io_entity = IOEntity(
                    io_id=io.id,
                    entity_id=entity.id,
                    role="mentioned",
                    mention_count=1,
                )
                self.session.add(io_entity)
            else:
                ie = existing_ie.scalar_one()
                ie.mention_count = (ie.mention_count or 0) + 1

        # 7. Update IO metadata
        io.last_source_added_at = datetime.now(timezone.utc)

        # Create initial version if this is a new IO
        if io.version_count == 0:
            await self._create_initial_version(io, source, text)

    async def _find_or_create_io(
        self,
        source: Source,
        text: str,
        embedding: list[float] | None,
        entities: list[Entity],
    ) -> IntelligenceObject:
        """Find an existing IO that matches this source, or create a new one."""

        # Try embedding-based clustering if we have an embedding
        if embedding:
            result = await self.session.execute(
                select(IntelligenceObject)
                .where(IntelligenceObject.status.in_(["draft", "review", "published"]))
                .where(IntelligenceObject.embedding.isnot(None))
                .order_by(IntelligenceObject.created_at.desc())
                .limit(100)
            )
            existing_ios = result.scalars().all()

            for io in existing_ios:
                if io.embedding is not None:
                    similarity = await compute_similarity(embedding, list(io.embedding))
                    if similarity > CLUSTERING_THRESHOLD:
                        logger.info(
                            "io_matched",
                            source_id=str(source.id),
                            io_id=str(io.id),
                            similarity=similarity,
                        )
                        return io

        # No match — create new IO
        category = classify_category(text)
        cantons = detect_cantons(text)
        scope = detect_scope(cantons, text)

        io = IntelligenceObject(
            category=category,
            scope=scope,
            canton_codes=cantons if cantons else None,
            status="draft",
            first_reported_at=source.original_published_at or datetime.now(timezone.utc),
            embedding=embedding,
        )
        self.session.add(io)
        await self.session.flush()

        logger.info(
            "io_created",
            io_id=str(io.id),
            category=category,
            scope=scope,
        )
        return io

    async def _create_initial_version(
        self, io: IntelligenceObject, source: Source, text: str
    ):
        """Create the initial version of an IO from its first source."""
        language = source.original_language or "de"

        content = {
            "title": source.original_title or "Untitled",
            "lead": source.snippet or "",
            "sections": [
                {
                    "type": "factual_core",
                    "content": source.snippet or source.original_title or "",
                    "attributions": [source.attribution_text],
                }
            ],
            "summary": source.snippet or "",
        }

        version = IOVersion(
            io_id=io.id,
            version_number=1,
            trigger_type="initial",
            trigger_source_ids=[source.id],
            review_status="pending",
            **{f"content_{language}": content},
        )
        self.session.add(version)
        await self.session.flush()

        io.current_version_id = version.id
        io.version_count = 1

"""Entity resolution — match extracted mentions to canonical entities."""

import uuid
from difflib import SequenceMatcher

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import Entity
from app.nlp.ner import EntityMention

logger = structlog.get_logger()


class EntityResolver:
    """Resolves entity mentions to canonical entities in the knowledge graph."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._cache: dict[str, Entity | None] = {}

    async def resolve(self, mention: EntityMention) -> Entity:
        """Resolve an entity mention to a canonical entity. Creates if not found."""
        # Check cache first
        cache_key = f"{mention.text}:{mention.entity_type}"
        if cache_key in self._cache:
            entity = self._cache[cache_key]
            if entity:
                return entity

        # 1. Exact match on canonical_name
        entity = await self._exact_match(mention.text, mention.entity_type)
        if entity:
            self._cache[cache_key] = entity
            return entity

        # 2. Match against aliases
        entity = await self._alias_match(mention.text, mention.entity_type)
        if entity:
            self._cache[cache_key] = entity
            return entity

        # 3. Fuzzy match
        entity = await self._fuzzy_match(mention.text, mention.entity_type)
        if entity:
            self._cache[cache_key] = entity
            return entity

        # 4. Create new entity
        entity = await self._create_entity(mention)
        self._cache[cache_key] = entity
        return entity

    async def _exact_match(self, name: str, entity_type: str) -> Entity | None:
        result = await self.session.execute(
            select(Entity).where(
                Entity.canonical_name == name,
                Entity.entity_type == entity_type,
            ).limit(1)
        )
        return result.scalar_one_or_none()

    async def _alias_match(self, name: str, entity_type: str) -> Entity | None:
        result = await self.session.execute(
            select(Entity).where(
                Entity.entity_type == entity_type,
                Entity.aliases.contains([name]),
            ).limit(1)
        )
        return result.scalar_one_or_none()

    async def _fuzzy_match(self, name: str, entity_type: str) -> Entity | None:
        """Find entities with similar names (Levenshtein-like)."""
        result = await self.session.execute(
            select(Entity).where(Entity.entity_type == entity_type).limit(500)
        )
        entities = result.scalars().all()

        best_match = None
        best_ratio = 0.0

        for entity in entities:
            ratio = SequenceMatcher(None, name.lower(), entity.canonical_name.lower()).ratio()
            if ratio > 0.85 and ratio > best_ratio:
                best_match = entity
                best_ratio = ratio

            # Also check against all name variants
            for names_list in [entity.names_de, entity.names_fr, entity.names_it, entity.names_en]:
                if names_list:
                    for alt_name in names_list:
                        r = SequenceMatcher(None, name.lower(), alt_name.lower()).ratio()
                        if r > 0.85 and r > best_ratio:
                            best_match = entity
                            best_ratio = r

        if best_match:
            logger.info(
                "entity_fuzzy_matched",
                mention=name,
                canonical=best_match.canonical_name,
                ratio=best_ratio,
            )
            # Add as alias for future exact matches
            if best_match.aliases is None:
                best_match.aliases = []
            if name not in best_match.aliases:
                best_match.aliases = [*best_match.aliases, name]

        return best_match

    async def _create_entity(self, mention: EntityMention) -> Entity:
        """Create a new entity from a mention."""
        entity = Entity(
            entity_type=mention.entity_type,
            canonical_name=mention.text,
            names_de=[mention.text],
            aliases=[mention.text],
            mention_count=1,
        )
        self.session.add(entity)
        await self.session.flush()

        logger.info(
            "entity_created",
            name=mention.text,
            type=mention.entity_type,
            id=str(entity.id),
        )
        return entity

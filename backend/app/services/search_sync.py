"""Sync published IOs to Meilisearch for instant full-text search."""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.intelligence_object import IOVersion, IntelligenceObject

logger = structlog.get_logger()


async def sync_ios_to_meilisearch() -> int:
    """Sync all published IOs to Meilisearch index."""
    try:
        import meilisearch

        client = meilisearch.Client(settings.meili_url, settings.meili_master_key)

        # Create/configure index
        try:
            client.create_index("intelligence_objects", {"primaryKey": "id"})
        except Exception:
            pass  # Index may already exist

        index = client.index("intelligence_objects")
        index.update_filterable_attributes(["status", "category", "scope", "canton_codes"])
        index.update_sortable_attributes(["created_at", "updated_at"])
        index.update_searchable_attributes([
            "title_de", "title_fr", "title_it", "title_en",
            "lead_de", "lead_fr", "lead_it", "lead_en",
            "summary_de", "summary_fr", "summary_it", "summary_en",
            "category", "canton_codes",
        ])

        # Fetch published IOs
        engine = create_async_engine(settings.database_url)
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with factory() as session:
            result = await session.execute(
                select(IntelligenceObject)
                .where(IntelligenceObject.status == "published")
                .where(IntelligenceObject.current_version_id.isnot(None))
            )
            ios = result.scalars().all()

            documents = []
            for io in ios:
                ver_result = await session.execute(
                    select(IOVersion).where(IOVersion.id == io.current_version_id)
                )
                version = ver_result.scalar_one_or_none()
                if not version:
                    continue

                doc = {
                    "id": str(io.id),
                    "status": io.status,
                    "category": io.category,
                    "scope": io.scope,
                    "canton_codes": io.canton_codes or [],
                    "created_at": io.created_at.isoformat() if io.created_at else "",
                    "updated_at": io.updated_at.isoformat() if io.updated_at else "",
                }

                for lang in ["de", "fr", "it", "en"]:
                    content = getattr(version, f"content_{lang}", None)
                    if content and isinstance(content, dict):
                        doc[f"title_{lang}"] = content.get("title", "")
                        doc[f"lead_{lang}"] = content.get("lead", "")
                        doc[f"summary_{lang}"] = content.get("summary", "")

                documents.append(doc)

            if documents:
                index.add_documents(documents)

        await engine.dispose()

        logger.info("meilisearch_synced", count=len(documents))
        return len(documents)

    except Exception as e:
        logger.error("meilisearch_sync_error", error=str(e))
        return 0

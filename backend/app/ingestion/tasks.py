"""Celery tasks for the ingestion pipeline."""

import asyncio

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.ingestion.scheduler import celery_app

logger = structlog.get_logger()


def get_session_factory():
    engine = create_async_engine(settings.database_url)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False), engine


async def _run_connector(connector_class):
    """Run a single connector in an async context."""
    factory, engine = get_session_factory()
    async with factory() as session:
        connector = connector_class(session)
        try:
            sources = await connector.fetch()
            await session.commit()
            return len(sources)
        except Exception as e:
            await session.rollback()
            logger.error("connector_error", connector=connector_class.__name__, error=str(e))
            return 0
        finally:
            await connector.close()
    await engine.dispose()


@celery_app.task(name="app.ingestion.tasks.run_admin_ch")
def run_admin_ch():
    from app.ingestion.admin_ch import AdminChConnector

    count = asyncio.run(_run_connector(AdminChConnector))
    logger.info("task_complete", task="admin_ch", new_sources=count)
    return count


@celery_app.task(name="app.ingestion.tasks.run_opendata_swiss")
def run_opendata_swiss():
    from app.ingestion.opendata_swiss import OpenDataSwissConnector

    count = asyncio.run(_run_connector(OpenDataSwissConnector))
    logger.info("task_complete", task="opendata_swiss", new_sources=count)
    return count


@celery_app.task(name="app.ingestion.tasks.run_curia_vista")
def run_curia_vista():
    from app.ingestion.curia_vista import CuriaVistaConnector

    count = asyncio.run(_run_connector(CuriaVistaConnector))
    logger.info("task_complete", task="curia_vista", new_sources=count)
    return count


@celery_app.task(name="app.ingestion.tasks.run_sogc_shab")
def run_sogc_shab():
    from app.ingestion.sogc_shab import SogcShabConnector

    count = asyncio.run(_run_connector(SogcShabConnector))
    logger.info("task_complete", task="sogc_shab", new_sources=count)
    return count


@celery_app.task(name="app.ingestion.tasks.run_bfs")
def run_bfs():
    from app.ingestion.bfs import BfsConnector

    count = asyncio.run(_run_connector(BfsConnector))
    logger.info("task_complete", task="bfs", new_sources=count)
    return count


@celery_app.task(name="app.ingestion.tasks.run_rss_monitor")
def run_rss_monitor():
    from app.ingestion.rss_monitor import RssMonitor

    async def _run():
        factory, engine = get_session_factory()
        async with factory() as session:
            monitor = RssMonitor(session)
            try:
                sources = await monitor.fetch_all()
                await session.commit()
                return len(sources)
            except Exception as e:
                await session.rollback()
                logger.error("rss_monitor_error", error=str(e))
                return 0
            finally:
                await monitor.close()
        await engine.dispose()

    count = asyncio.run(_run())
    logger.info("task_complete", task="rss_monitor", new_sources=count)
    return count


@celery_app.task(name="app.ingestion.tasks.process_unprocessed_sources")
def process_unprocessed_sources():
    """Process sources that haven't been assigned to IOs yet."""
    from app.nlp.pipeline import ProcessingPipeline

    async def _run():
        factory, engine = get_session_factory()
        async with factory() as session:
            pipeline = ProcessingPipeline(session)
            count = await pipeline.process_batch()
            await session.commit()
            return count
        await engine.dispose()

    count = asyncio.run(_run())
    logger.info("task_complete", task="process_sources", processed=count)
    return count


@celery_app.task(name="app.ingestion.tasks.sync_search_index")
def sync_search_index():
    """Sync published IOs to Meilisearch index."""
    from app.services.search_sync import sync_ios_to_meilisearch

    count = asyncio.run(sync_ios_to_meilisearch())
    logger.info("task_complete", task="search_sync", indexed=count)
    return count

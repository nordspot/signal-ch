"""Celery task scheduler for ingestion jobs."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery("signal", broker=settings.redis_url, backend=settings.redis_url)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Zurich",
    enable_utc=True,
    task_track_started=True,
    task_default_queue="ingestion",
    worker_prefetch_multiplier=1,
)

# Beat schedule — matches priority table from spec §7
celery_app.conf.beat_schedule = {
    # P2: RSS monitoring every 15 minutes
    "rss-monitor": {
        "task": "app.ingestion.tasks.run_rss_monitor",
        "schedule": 900.0,  # 15 minutes
    },
    # P3: Government publications every hour
    "admin-ch": {
        "task": "app.ingestion.tasks.run_admin_ch",
        "schedule": 1800.0,  # 30 minutes
    },
    "curia-vista": {
        "task": "app.ingestion.tasks.run_curia_vista",
        "schedule": 3600.0,  # 1 hour
    },
    "bfs": {
        "task": "app.ingestion.tasks.run_bfs",
        "schedule": 3600.0,  # 1 hour
    },
    # P4: Periodic sources every 6 hours
    "opendata-swiss": {
        "task": "app.ingestion.tasks.run_opendata_swiss",
        "schedule": 21600.0,  # 6 hours
    },
    "sogc-shab": {
        "task": "app.ingestion.tasks.run_sogc_shab",
        "schedule": 21600.0,  # 6 hours
    },
    # Process unprocessed sources every 5 minutes
    "process-sources": {
        "task": "app.ingestion.tasks.process_unprocessed_sources",
        "schedule": 300.0,  # 5 minutes
    },
    # Daily Meilisearch index sync
    "sync-search-index": {
        "task": "app.ingestion.tasks.sync_search_index",
        "schedule": crontab(hour=3, minute=0),  # 3 AM
    },
}

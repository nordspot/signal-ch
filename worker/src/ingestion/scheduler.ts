import type { Env } from '../types';
import { parseJson } from '../utils';

export async function runScheduledIngestion(
  event: ScheduledEvent,
  env: Env
): Promise<void> {
  const cron = event.cron;

  if (cron === '*/30 * * * *') {
    // Every 30 minutes: ingest government APIs + active RSS feeds
    await triggerGovernmentIngestion(env);
    await triggerRssIngestion(env);
  } else if (cron === '0 3 * * *') {
    // Daily at 3 AM: maintenance tasks
    await runDailyMaintenance(env);
  }
}

async function triggerGovernmentIngestion(env: Env): Promise<void> {
  const connectors = ['admin_ch', 'curia_vista', 'opendata_swiss', 'sogc', 'bfs'];

  for (const connector of connectors) {
    await env.INGESTION_QUEUE.send({
      type: 'ingest_api',
      payload: { connector },
    });
  }
}

async function triggerRssIngestion(env: Env): Promise<void> {
  // Get all publishers with RSS feeds
  const publishers = await env.DB.prepare(
    "SELECT id, rss_feeds FROM publishers WHERE rss_feeds IS NOT NULL AND rss_feeds != '[]'"
  ).all();

  for (const pub of publishers.results) {
    const feeds = parseJson<{ url: string; language: string; category?: string }[]>(
      pub.rss_feeds as string, []
    );

    for (const feed of feeds) {
      await env.INGESTION_QUEUE.send({
        type: 'ingest_rss',
        payload: {
          publisher_id: pub.id,
          feed_url: feed.url,
          language: feed.language,
        },
      });
    }
  }
}

async function runDailyMaintenance(env: Env): Promise<void> {
  // 1. Clean up old unprocessed sources (>7 days)
  await env.DB.prepare(
    "DELETE FROM sources WHERE processed = 0 AND created_at < datetime('now', '-7 days')"
  ).run();

  // 2. Update entity mention counts
  await env.DB.prepare(
    `UPDATE entities SET mention_count = (
      SELECT COUNT(*) FROM io_entities WHERE entity_id = entities.id
    )`
  ).run();

  // 3. Recalculate confirmation density for active IOs
  const activeIOs = await env.DB.prepare(
    "SELECT id FROM intelligence_objects WHERE updated_at >= datetime('now', '-7 days')"
  ).all();

  for (const io of activeIOs.results) {
    const sourceCount = await env.DB.prepare(
      'SELECT COUNT(*) as c FROM sources WHERE assigned_io_id = ?'
    ).bind(io.id).first();

    const publisherCount = await env.DB.prepare(
      'SELECT COUNT(DISTINCT publisher_id) as c FROM sources WHERE assigned_io_id = ?'
    ).bind(io.id).first();

    const density = Math.min(((sourceCount?.c as number) || 0) / 5, 1);
    const diversity = Math.min(((publisherCount?.c as number) || 0) / 3, 1);

    await env.DB.prepare(
      'UPDATE intelligence_objects SET confirmation_density = ?, source_diversity = ? WHERE id = ?'
    ).bind(density, diversity, io.id).run();
  }

  // 4. Sync published IOs to search index
  const unsyncedIOs = await env.DB.prepare(
    `SELECT id FROM intelligence_objects
     WHERE status = 'published'
     AND updated_at >= datetime('now', '-1 day')`
  ).all();

  for (const io of unsyncedIOs.results) {
    await env.INGESTION_QUEUE.send({
      type: 'sync_search',
      payload: { io_id: io.id },
    });
  }
}

import { Hono } from 'hono';
import type { Env } from '../types';
import { getUser, requireEditor } from '../auth';
import { parseJson, now } from '../utils';

export function adminRoutes() {
  const app = new Hono<{ Bindings: Env }>();

  app.get('/stats', async (c) => {
    const user = requireEditor(await getUser(c.env, c.req.raw));

    const [ios, published, pending, sources, publishers, users] = await Promise.all([
      c.env.DB.prepare('SELECT COUNT(*) as c FROM intelligence_objects').first(),
      c.env.DB.prepare("SELECT COUNT(*) as c FROM intelligence_objects WHERE status = 'published'").first(),
      c.env.DB.prepare("SELECT COUNT(*) as c FROM io_versions WHERE review_status = 'pending'").first(),
      c.env.DB.prepare('SELECT COUNT(*) as c FROM sources').first(),
      c.env.DB.prepare('SELECT COUNT(*) as c FROM publishers').first(),
      c.env.DB.prepare('SELECT COUNT(*) as c FROM users').first(),
    ]);

    return c.json({
      total_ios: (ios?.c as number) || 0,
      published_ios: (published?.c as number) || 0,
      pending_reviews: (pending?.c as number) || 0,
      total_sources: (sources?.c as number) || 0,
      total_publishers: (publishers?.c as number) || 0,
      total_users: (users?.c as number) || 0,
    });
  });

  app.get('/review-queue', async (c) => {
    const user = requireEditor(await getUser(c.env, c.req.raw));
    const page = parseInt(c.req.query('page') || '1');
    const pageSize = 20;

    const rows = await c.env.DB.prepare(
      `SELECT v.*, io.category as io_category, io.status as io_status
       FROM io_versions v
       JOIN intelligence_objects io ON v.io_id = io.id
       WHERE v.review_status = 'pending'
       ORDER BY v.created_at ASC
       LIMIT ? OFFSET ?`
    ).bind(pageSize, (page - 1) * pageSize).all();

    return c.json({
      items: rows.results.map((v) => ({
        version_id: v.id,
        io_id: v.io_id,
        version_number: v.version_number,
        trigger_type: v.trigger_type,
        created_at: v.created_at,
        content_de: parseJson(v.content_de as string, null),
        content_fr: parseJson(v.content_fr as string, null),
        content_it: parseJson(v.content_it as string, null),
        content_en: parseJson(v.content_en as string, null),
        io_category: v.io_category,
        io_status: v.io_status,
      })),
      page,
    });
  });

  app.post('/review/:versionId', async (c) => {
    const user = requireEditor(await getUser(c.env, c.req.raw));
    const versionId = c.req.param('versionId');
    const { action, notes } = await c.req.json();

    if (!['approved', 'rejected'].includes(action)) {
      return c.json({ error: 'Invalid action' }, 400);
    }

    // Update version
    await c.env.DB.prepare(
      `UPDATE io_versions SET review_status = ?, reviewed_by = ?, reviewed_at = ? WHERE id = ?`
    ).bind(action, user.id, now(), versionId).run();

    // If approved, publish the IO
    if (action === 'approved') {
      const version = await c.env.DB.prepare('SELECT io_id FROM io_versions WHERE id = ?').bind(versionId).first();
      if (version) {
        await c.env.DB.prepare(
          `UPDATE intelligence_objects SET current_version_id = ?, status = 'published', updated_at = ? WHERE id = ?`
        ).bind(versionId, now(), version.io_id).run();

        // Upsert to Vectorize
        try {
          const io = await c.env.DB.prepare('SELECT * FROM intelligence_objects WHERE id = ?').bind(version.io_id).first();
          if (io) {
            await c.env.VECTORIZE.upsert([{
              id: io.id as string,
              values: new Array(1024).fill(0), // placeholder — real embedding from Cohere
              metadata: { status: 'published', category: io.category as string },
            }]);
          }
        } catch { /* vectorize optional */ }
      }
    }

    return c.json({ status: 'ok', review_status: action });
  });

  return app;
}

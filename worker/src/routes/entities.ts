import { Hono } from 'hono';
import type { Env } from '../types';
import { parseJson } from '../utils';

export function entitiesRoutes() {
  const app = new Hono<{ Bindings: Env }>();

  app.get('/', async (c) => {
    const entityType = c.req.query('entity_type');
    const q = c.req.query('q');
    const page = parseInt(c.req.query('page') || '1');
    const pageSize = Math.min(parseInt(c.req.query('page_size') || '20'), 100);

    let where = 'WHERE 1=1';
    const params: unknown[] = [];

    if (entityType) { where += ' AND entity_type = ?'; params.push(entityType); }
    if (q) { where += ' AND canonical_name LIKE ?'; params.push(`%${q}%`); }

    const countResult = await c.env.DB.prepare(
      `SELECT COUNT(*) as total FROM entities ${where}`
    ).bind(...params).first();

    const rows = await c.env.DB.prepare(
      `SELECT * FROM entities ${where} ORDER BY mention_count DESC LIMIT ? OFFSET ?`
    ).bind(...params, pageSize, (page - 1) * pageSize).all();

    return c.json({
      items: rows.results.map((e) => ({
        id: e.id, entity_type: e.entity_type, canonical_name: e.canonical_name,
        names_de: parseJson(e.names_de as string, null),
        names_fr: parseJson(e.names_fr as string, null),
        names_it: parseJson(e.names_it as string, null),
        names_en: parseJson(e.names_en as string, null),
        aliases: parseJson(e.aliases as string, null),
        metadata: parseJson(e.metadata as string, {}),
        wikidata_id: e.wikidata_id, mention_count: e.mention_count,
        last_mentioned_at: e.last_mentioned_at,
      })),
      total: (countResult?.total as number) || 0,
    });
  });

  app.get('/:id', async (c) => {
    const row = await c.env.DB.prepare('SELECT * FROM entities WHERE id = ?').bind(c.req.param('id')).first();
    if (!row) return c.json({ error: 'Not found' }, 404);
    return c.json({
      id: row.id, entity_type: row.entity_type, canonical_name: row.canonical_name,
      names_de: parseJson(row.names_de as string, null),
      names_fr: parseJson(row.names_fr as string, null),
      names_it: parseJson(row.names_it as string, null),
      names_en: parseJson(row.names_en as string, null),
      aliases: parseJson(row.aliases as string, null),
      metadata: parseJson(row.metadata as string, {}),
      wikidata_id: row.wikidata_id, mention_count: row.mention_count,
      last_mentioned_at: row.last_mentioned_at,
    });
  });

  app.get('/:id/ios', async (c) => {
    const rows = await c.env.DB.prepare(
      `SELECT io.* FROM intelligence_objects io
       JOIN io_entities ie ON ie.io_id = io.id
       WHERE ie.entity_id = ? AND io.status = 'published'
       ORDER BY io.created_at DESC LIMIT 50`
    ).bind(c.req.param('id')).all();

    return c.json(rows.results.map((io) => ({
      id: io.id, status: io.status, category: io.category, scope: io.scope,
      canton_codes: parseJson(io.canton_codes as string, null),
      confirmation_density: io.confirmation_density,
      version_count: io.version_count, created_at: io.created_at,
      first_reported_at: io.first_reported_at,
    })));
  });

  app.get('/:id/relations', async (c) => {
    const id = c.req.param('id');
    const rows = await c.env.DB.prepare(
      `SELECT * FROM entity_relations WHERE source_entity_id = ? OR target_entity_id = ?`
    ).bind(id, id).all();

    return c.json(rows.results.map((r) => ({
      id: r.id, source_entity_id: r.source_entity_id, target_entity_id: r.target_entity_id,
      relation_type: r.relation_type, confidence: r.confidence,
      valid_from: r.valid_from, valid_to: r.valid_to,
    })));
  });

  return app;
}

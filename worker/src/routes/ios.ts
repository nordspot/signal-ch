import { Hono } from 'hono';
import type { Env } from '../types';
import { getUser } from '../auth';
import { parseJson } from '../utils';

export function iosRoutes() {
  const app = new Hono<{ Bindings: Env }>();

  // List IOs
  app.get('/', async (c) => {
    const category = c.req.query('category');
    const scope = c.req.query('scope');
    const canton = c.req.query('canton');
    const status = c.req.query('status') || 'published';
    const page = parseInt(c.req.query('page') || '1');
    const pageSize = Math.min(parseInt(c.req.query('page_size') || '20'), 100);
    const offset = (page - 1) * pageSize;

    let where = 'WHERE status = ?';
    const params: unknown[] = [status];

    if (category) { where += ' AND category = ?'; params.push(category); }
    if (scope) { where += ' AND scope = ?'; params.push(scope); }
    if (canton) { where += " AND canton_codes LIKE '%\"' || ? || '\"%'"; params.push(canton); }

    const countResult = await c.env.DB.prepare(
      `SELECT COUNT(*) as total FROM intelligence_objects ${where}`
    ).bind(...params).first();
    const total = (countResult?.total as number) || 0;

    const rows = await c.env.DB.prepare(
      `SELECT io.*, v.id as ver_id, v.version_number, v.content_de, v.content_fr, v.content_it, v.content_en,
              v.trigger_type, v.review_status, v.created_at as ver_created_at
       FROM intelligence_objects io
       LEFT JOIN io_versions v ON io.current_version_id = v.id
       ${where}
       ORDER BY io.created_at DESC
       LIMIT ? OFFSET ?`
    ).bind(...params, pageSize, offset).all();

    const items = rows.results.map((row) => ({
      id: row.id,
      created_at: row.created_at,
      updated_at: row.updated_at,
      status: row.status,
      category: row.category,
      subcategory: row.subcategory,
      scope: row.scope,
      canton_codes: parseJson(row.canton_codes as string, null),
      confirmation_density: row.confirmation_density,
      source_diversity: row.source_diversity,
      completeness_score: row.completeness_score,
      bias_spectrum: parseJson(row.bias_spectrum as string, {}),
      missing_elements: parseJson(row.missing_elements as string, null),
      version_count: row.version_count,
      first_reported_at: row.first_reported_at,
      current_version: row.ver_id ? {
        id: row.ver_id,
        version_number: row.version_number,
        created_at: row.ver_created_at,
        content_de: parseJson(row.content_de as string, null),
        content_fr: parseJson(row.content_fr as string, null),
        content_it: parseJson(row.content_it as string, null),
        content_en: parseJson(row.content_en as string, null),
        trigger_type: row.trigger_type,
        review_status: row.review_status,
      } : null,
    }));

    return c.json({ items, total, page, page_size: pageSize });
  });

  // Get single IO
  app.get('/:id', async (c) => {
    const id = c.req.param('id');
    const row = await c.env.DB.prepare(
      `SELECT io.*, v.id as ver_id, v.version_number, v.content_de, v.content_fr, v.content_it, v.content_en,
              v.trigger_type, v.review_status, v.diff_summary, v.created_at as ver_created_at
       FROM intelligence_objects io
       LEFT JOIN io_versions v ON io.current_version_id = v.id
       WHERE io.id = ?`
    ).bind(id).first();

    if (!row) return c.json({ error: 'Not found' }, 404);

    return c.json({
      id: row.id,
      created_at: row.created_at,
      updated_at: row.updated_at,
      status: row.status,
      category: row.category,
      subcategory: row.subcategory,
      scope: row.scope,
      canton_codes: parseJson(row.canton_codes as string, null),
      confirmation_density: row.confirmation_density,
      source_diversity: row.source_diversity,
      completeness_score: row.completeness_score,
      bias_spectrum: parseJson(row.bias_spectrum as string, {}),
      missing_elements: parseJson(row.missing_elements as string, null),
      version_count: row.version_count,
      first_reported_at: row.first_reported_at,
      current_version: row.ver_id ? {
        id: row.ver_id,
        version_number: row.version_number,
        created_at: row.ver_created_at,
        content_de: parseJson(row.content_de as string, null),
        content_fr: parseJson(row.content_fr as string, null),
        content_it: parseJson(row.content_it as string, null),
        content_en: parseJson(row.content_en as string, null),
        trigger_type: row.trigger_type,
        review_status: row.review_status,
        diff_summary: parseJson(row.diff_summary as string, null),
      } : null,
    });
  });

  // Get IO versions
  app.get('/:id/versions', async (c) => {
    const id = c.req.param('id');
    const rows = await c.env.DB.prepare(
      `SELECT * FROM io_versions WHERE io_id = ? ORDER BY version_number DESC`
    ).bind(id).all();

    return c.json(rows.results.map((v) => ({
      id: v.id,
      version_number: v.version_number,
      created_at: v.created_at,
      content_de: parseJson(v.content_de as string, null),
      content_fr: parseJson(v.content_fr as string, null),
      content_it: parseJson(v.content_it as string, null),
      content_en: parseJson(v.content_en as string, null),
      trigger_type: v.trigger_type,
      review_status: v.review_status,
      diff_summary: parseJson(v.diff_summary as string, null),
    })));
  });

  // Get IO sources
  app.get('/:id/sources', async (c) => {
    const id = c.req.param('id');
    const rows = await c.env.DB.prepare(
      `SELECT s.*, ios.contribution_type
       FROM sources s
       JOIN io_sources ios ON ios.source_id = s.id
       WHERE ios.io_id = ?
       ORDER BY s.original_published_at DESC`
    ).bind(id).all();

    return c.json(rows.results.map((s) => ({
      id: s.id, source_type: s.source_type, license_status: s.license_status,
      original_url: s.original_url, original_title: s.original_title,
      original_language: s.original_language, original_published_at: s.original_published_at,
      snippet: s.snippet, attribution_text: s.attribution_text, author_name: s.author_name,
      publisher_reliability_score: s.publisher_reliability_score,
      contribution_type: s.contribution_type,
    })));
  });

  return app;
}

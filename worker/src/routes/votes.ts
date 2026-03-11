import { Hono } from 'hono';
import type { Env } from '../types';
import { parseJson } from '../utils';

export function votesRoutes() {
  const app = new Hono<{ Bindings: Env }>();

  app.get('/', async (c) => {
    const status = c.req.query('status');
    const level = c.req.query('level');
    const canton = c.req.query('canton');
    const limit = Math.min(parseInt(c.req.query('limit') || '20'), 100);

    let where = 'WHERE 1=1';
    const params: unknown[] = [];
    if (status) { where += ' AND status = ?'; params.push(status); }
    if (level) { where += ' AND level = ?'; params.push(level); }
    if (canton) { where += ' AND canton = ?'; params.push(canton); }

    const rows = await c.env.DB.prepare(
      `SELECT * FROM votes_and_initiatives ${where} ORDER BY vote_date DESC LIMIT ?`
    ).bind(...params, limit).all();

    return c.json(rows.results.map((v) => ({
      id: v.id, vote_type: v.vote_type, level: v.level, canton: v.canton,
      title_de: v.title_de, title_fr: v.title_fr, title_it: v.title_it,
      official_url: v.official_url, vote_date: v.vote_date, status: v.status,
      result: parseJson(v.result as string, null),
      pro_arguments: parseJson(v.pro_arguments as string, null),
      contra_arguments: parseJson(v.contra_arguments as string, null),
    })));
  });

  app.get('/:id', async (c) => {
    const row = await c.env.DB.prepare('SELECT * FROM votes_and_initiatives WHERE id = ?').bind(c.req.param('id')).first();
    if (!row) return c.json({ error: 'Not found' }, 404);
    return c.json({
      id: row.id, vote_type: row.vote_type, level: row.level, canton: row.canton,
      title_de: row.title_de, title_fr: row.title_fr, title_it: row.title_it,
      official_url: row.official_url, vote_date: row.vote_date, status: row.status,
      result: parseJson(row.result as string, null),
      pro_arguments: parseJson(row.pro_arguments as string, null),
      contra_arguments: parseJson(row.contra_arguments as string, null),
      financial_impact: parseJson(row.financial_impact as string, null),
    });
  });

  return app;
}

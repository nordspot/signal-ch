import { Hono } from 'hono';
import type { Env } from '../types';
import { parseJson } from '../utils';

export function searchRoutes() {
  const app = new Hono<{ Bindings: Env }>();

  app.get('/', async (c) => {
    const q = c.req.query('q');
    if (!q || q.length < 2) return c.json({ error: 'Query too short' }, 400);

    const limit = Math.min(parseInt(c.req.query('limit') || '20'), 100);
    const category = c.req.query('category');

    // Try vector search first via Vectorize
    try {
      // Generate query embedding
      const embedding = await generateQueryEmbedding(q, c.env);
      if (embedding) {
        const vectorResults = await c.env.VECTORIZE.query(embedding, {
          topK: limit,
          filter: { status: 'published' },
          returnMetadata: 'all',
        });

        if (vectorResults.matches.length > 0) {
          const ids = vectorResults.matches.map(m => m.id);
          const placeholders = ids.map(() => '?').join(',');
          const rows = await c.env.DB.prepare(
            `SELECT * FROM intelligence_objects WHERE id IN (${placeholders}) AND status = 'published'`
          ).bind(...ids).all();

          return c.json(rows.results.map((io) => ({
            id: io.id, status: io.status, category: io.category, scope: io.scope,
            canton_codes: parseJson(io.canton_codes as string, null),
            confirmation_density: io.confirmation_density,
            version_count: io.version_count, created_at: io.created_at,
            bias_spectrum: parseJson(io.bias_spectrum as string, {}),
          })));
        }
      }
    } catch {
      // Fall through to text search
    }

    // Fallback: text search via D1 FTS
    let where = "WHERE status = 'published'";
    const params: unknown[] = [];

    // Search in version content titles
    const rows = await c.env.DB.prepare(
      `SELECT DISTINCT io.* FROM intelligence_objects io
       LEFT JOIN io_versions v ON io.current_version_id = v.id
       WHERE io.status = 'published'
       AND (v.content_de LIKE ? OR v.content_fr LIKE ? OR v.content_it LIKE ? OR v.content_en LIKE ?)
       ORDER BY io.created_at DESC
       LIMIT ?`
    ).bind(`%${q}%`, `%${q}%`, `%${q}%`, `%${q}%`, limit).all();

    return c.json(rows.results.map((io) => ({
      id: io.id, status: io.status, category: io.category, scope: io.scope,
      canton_codes: parseJson(io.canton_codes as string, null),
      confirmation_density: io.confirmation_density,
      version_count: io.version_count, created_at: io.created_at,
      bias_spectrum: parseJson(io.bias_spectrum as string, {}),
    })));
  });

  return app;
}

async function generateQueryEmbedding(text: string, env: Env): Promise<number[] | null> {
  if (!env.COHERE_API_KEY) return null;

  try {
    const response = await fetch('https://api.cohere.ai/v1/embed', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.COHERE_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        texts: [text],
        model: 'embed-multilingual-v3.0',
        input_type: 'search_query',
        embedding_types: ['float'],
      }),
    });

    const data = await response.json() as any;
    return data.embeddings?.float?.[0] ?? null;
  } catch {
    return null;
  }
}

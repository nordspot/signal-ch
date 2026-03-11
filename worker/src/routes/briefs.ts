import { Hono } from 'hono';
import type { Env } from '../types';
import { getUser } from '../auth';
import { parseJson } from '../utils';

export function briefsRoutes() {
  const app = new Hono<{ Bindings: Env }>();

  app.get('/daily', async (c) => {
    const language = c.req.query('language') || 'de';
    const user = await getUser(c.env, c.req.raw);

    // Get top published IOs from last 24 hours
    const rows = await c.env.DB.prepare(
      `SELECT io.*, v.content_de, v.content_fr, v.content_it, v.content_en
       FROM intelligence_objects io
       LEFT JOIN io_versions v ON io.current_version_id = v.id
       WHERE io.status = 'published'
       AND io.updated_at >= datetime('now', '-1 day')
       ORDER BY io.confirmation_density DESC, io.created_at DESC
       LIMIT 10`
    ).all();

    const greetings: Record<string, string> = {
      de: 'Guten Morgen. Hier ist Ihr Signal-Briefing.',
      fr: 'Bonjour. Voici votre briefing Signal.',
      it: 'Buongiorno. Ecco il vostro briefing Signal.',
      en: "Good morning. Here's your Signal briefing.",
    };

    const stories = rows.results.map((row) => {
      const contentKey = `content_${language}` as string;
      const content = parseJson(row[contentKey] as string, null) || parseJson(row.content_de as string, null);
      return {
        io_id: row.id,
        category: row.category,
        title: content?.title || 'Untitled',
        summary: content?.summary || content?.lead || '',
      };
    });

    return c.json({
      greeting: greetings[language] || greetings.de,
      date: new Date().toLocaleDateString('de-CH'),
      top_stories: stories,
      developing: [],
      watch_today: '',
      closing: 'Bleiben Sie informiert. Signal.ch',
    });
  });

  return app;
}

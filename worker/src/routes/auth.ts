import { Hono } from 'hono';
import type { Env } from '../types';
import { createToken, getUser, hashPassword, verifyPassword } from '../auth';
import { uuid, now } from '../utils';

export function authRoutes() {
  const app = new Hono<{ Bindings: Env }>();

  app.post('/register', async (c) => {
    const { email, password, display_name, preferred_language, canton } = await c.req.json();
    if (!email || !password) return c.json({ error: 'Email and password required' }, 400);

    const existing = await c.env.DB.prepare('SELECT id FROM users WHERE email = ?').bind(email).first();
    if (existing) return c.json({ error: 'Email already registered' }, 400);

    const id = uuid();
    const hash = await hashPassword(password);

    await c.env.DB.prepare(
      `INSERT INTO users (id, email, password_hash, auth_provider, display_name, preferred_language, canton, created_at)
       VALUES (?, ?, ?, 'email', ?, ?, ?, ?)`
    ).bind(id, email, hash, display_name || null, preferred_language || 'de', canton || null, now()).run();

    const token = await createToken(id, c.env.JWT_SECRET);
    return c.json({
      access_token: token,
      token_type: 'bearer',
      user: { id, email, display_name, preferred_language: preferred_language || 'de', canton, tier: 'free', created_at: now() },
    }, 201);
  });

  app.post('/login', async (c) => {
    const { email, password } = await c.req.json();
    if (!email || !password) return c.json({ error: 'Email and password required' }, 400);

    const user = await c.env.DB.prepare(
      'SELECT id, email, password_hash, display_name, preferred_language, canton, tier, created_at FROM users WHERE email = ?'
    ).bind(email).first();

    if (!user || !user.password_hash) return c.json({ error: 'Invalid credentials' }, 401);
    if (!(await verifyPassword(password, user.password_hash as string))) {
      return c.json({ error: 'Invalid credentials' }, 401);
    }

    const token = await createToken(user.id as string, c.env.JWT_SECRET);
    return c.json({
      access_token: token,
      token_type: 'bearer',
      user: {
        id: user.id, email: user.email, display_name: user.display_name,
        preferred_language: user.preferred_language, canton: user.canton,
        tier: user.tier, created_at: user.created_at,
      },
    });
  });

  app.get('/me', async (c) => {
    const user = await getUser(c.env, c.req.raw);
    if (!user) return c.json({ error: 'Not authenticated' }, 401);
    return c.json(user);
  });

  return app;
}

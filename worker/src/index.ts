import { Hono } from 'hono';
import { cors } from 'hono/cors';
import type { Env, QueueMessage } from './types';
import { authRoutes } from './routes/auth';
import { iosRoutes } from './routes/ios';
import { entitiesRoutes } from './routes/entities';
import { searchRoutes } from './routes/search';
import { votesRoutes } from './routes/votes';
import { briefsRoutes } from './routes/briefs';
import { adminRoutes } from './routes/admin';
import { handleIngestionQueue } from './ingestion/queue';
import { runScheduledIngestion } from './ingestion/scheduler';

const app = new Hono<{ Bindings: Env }>();

// CORS
app.use('*', cors({
  origin: ['https://signal.ch', 'https://signal-ch.pages.dev', 'http://localhost:3000'],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowHeaders: ['Content-Type', 'Authorization'],
}));

// Health
app.get('/', (c) => c.json({
  name: 'Signal.ch API',
  version: '0.1.0',
  docs: '/v1',
}));

app.get('/health', (c) => c.json({ status: 'ok', service: 'signal-api' }));

// Mount routes
app.route('/v1/auth', authRoutes());
app.route('/v1/ios', iosRoutes());
app.route('/v1/entities', entitiesRoutes());
app.route('/v1/search', searchRoutes());
app.route('/v1/votes', votesRoutes());
app.route('/v1/briefs', briefsRoutes());
app.route('/v1/admin', adminRoutes());

export default {
  fetch: app.fetch,

  // Queue consumer for async ingestion jobs
  async queue(batch: MessageBatch<QueueMessage>, env: Env): Promise<void> {
    await handleIngestionQueue(batch, env);
  },

  // Cron trigger for scheduled ingestion
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    ctx.waitUntil(runScheduledIngestion(event, env));
  },
};

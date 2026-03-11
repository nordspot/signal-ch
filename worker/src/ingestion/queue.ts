import type { Env, QueueMessage } from '../types';
import { uuid, now, jsonCol } from '../utils';

// Route a message: use Queue if available, otherwise process directly
async function enqueue(env: Env, msg: QueueMessage): Promise<void> {
  if (env.INGESTION_QUEUE) {
    await env.INGESTION_QUEUE.send(msg);
  } else {
    await dispatchMessage(msg, env);
  }
}

export async function dispatchMessage(msg: QueueMessage, env: Env): Promise<void> {
  switch (msg.type) {
    case 'ingest_rss': await ingestRssFeed(msg.payload, env); break;
    case 'ingest_api': await ingestApiSource(msg.payload, env); break;
    case 'process_source': await processSource(msg.payload, env); break;
    case 'synthesize_io': await synthesizeIO(msg.payload, env); break;
    case 'sync_search': await syncSearchIndex(msg.payload, env); break;
  }
}

export async function handleIngestionQueue(
  batch: MessageBatch<QueueMessage>,
  env: Env
): Promise<void> {
  for (const msg of batch.messages) {
    try {
      await dispatchMessage(msg.body, env);
      msg.ack();
    } catch (e) {
      console.error(`Queue message failed: ${msg.body.type}`, e);
      msg.retry();
    }
  }
}

// --- RSS Feed Ingestion ---

async function ingestRssFeed(payload: Record<string, unknown>, env: Env): Promise<void> {
  const publisherId = payload.publisher_id as string;
  const feedUrl = payload.feed_url as string;
  const language = (payload.language as string) || 'de';

  const publisher = await env.DB.prepare(
    'SELECT * FROM publishers WHERE id = ?'
  ).bind(publisherId).first();
  if (!publisher) return;

  // Fetch and parse RSS
  const response = await fetch(feedUrl, {
    headers: { 'User-Agent': 'Signal.ch/0.1 (news intelligence; contact@signal.ch)' },
  });
  if (!response.ok) return;

  const xml = await response.text();
  const items = parseRssItems(xml);

  for (const item of items.slice(0, 20)) {
    // Check if source already exists by URL
    const existing = await env.DB.prepare(
      'SELECT id FROM sources WHERE original_url = ?'
    ).bind(item.link).first();
    if (existing) continue;

    const sourceId = uuid();
    const licenseAllowsSynthesis = publisher.license_allows_synthesis ? 1 : 0;
    const licenseAllowsFullText = publisher.license_allows_full_text ? 1 : 0;

    await env.DB.prepare(
      `INSERT INTO sources (id, source_type, license_status, can_display_full_text, can_synthesize_from,
       original_url, original_title, original_language, original_published_at, snippet,
       publisher_id, attribution_text, processed, created_at)
       VALUES (?, 'rss', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)`
    ).bind(
      sourceId,
      publisher.license_type || 'unknown',
      licenseAllowsFullText,
      licenseAllowsSynthesis,
      item.link,
      item.title,
      language,
      item.pubDate || now(),
      item.description?.slice(0, 500) || null,
      publisherId,
      `${publisher.name} – ${item.title}`,
      now()
    ).run();

    // Enqueue source processing
    await enqueue(env, {
      type: 'process_source',
      payload: { source_id: sourceId },
    });
  }
}

// --- Government API Ingestion ---

async function ingestApiSource(payload: Record<string, unknown>, env: Env): Promise<void> {
  const connector = payload.connector as string;

  switch (connector) {
    case 'admin_ch':
      await ingestAdminCh(env);
      break;
    case 'curia_vista':
      await ingestCuriaVista(env);
      break;
    case 'opendata_swiss':
      await ingestOpendataSwiss(env);
      break;
    case 'sogc':
      await ingestSOGC(env);
      break;
    case 'bfs':
      await ingestBFS(env);
      break;
  }
}

async function ingestAdminCh(env: Env): Promise<void> {
  // Federal Council press releases
  const response = await fetch(
    'https://www.admin.ch/gov/de/start/dokumentation/medienmitteilungen.msg-id.html?format=json&pageSize=20',
    { headers: { 'User-Agent': 'Signal.ch/0.1' } }
  );
  if (!response.ok) return;

  const data = await response.json() as any;
  const items = data?.items || data?.results || [];

  for (const item of items.slice(0, 20)) {
    const url = item.url || item.link || `https://www.admin.ch/id/${item.id}`;
    const existing = await env.DB.prepare(
      'SELECT id FROM sources WHERE original_url = ?'
    ).bind(url).first();
    if (existing) continue;

    const sourceId = uuid();
    await env.DB.prepare(
      `INSERT INTO sources (id, source_type, license_status, can_display_full_text, can_synthesize_from,
       original_url, original_title, original_language, original_published_at, snippet,
       publisher_id, attribution_text, processed, created_at)
       VALUES (?, 'government_api', 'open_government', 1, 1, ?, ?, 'de', ?, ?, ?, ?, 0, ?)`
    ).bind(
      sourceId, url,
      item.title || 'Federal Council communication',
      item.date || now(),
      (item.lead || item.description || '').slice(0, 500),
      'gov-admin-ch',
      `Schweizerische Eidgenossenschaft – ${item.title || ''}`,
      now()
    ).run();

    await enqueue(env, {
      type: 'process_source',
      payload: { source_id: sourceId },
    });
  }
}

async function ingestCuriaVista(env: Env): Promise<void> {
  // Parliamentary business from Curia Vista OData API
  const response = await fetch(
    'https://ws.parlament.ch/odata.svc/Business?$top=20&$orderby=SubmissionDate desc&$format=json',
    { headers: { 'User-Agent': 'Signal.ch/0.1' } }
  );
  if (!response.ok) return;

  const data = await response.json() as any;
  const items = data?.d?.results || data?.value || [];

  for (const item of items) {
    const url = `https://www.parlament.ch/de/ratsbetrieb/suche-curia-vista/geschaeft?AffairId=${item.ID || item.Id}`;
    const existing = await env.DB.prepare(
      'SELECT id FROM sources WHERE original_url = ?'
    ).bind(url).first();
    if (existing) continue;

    const sourceId = uuid();
    await env.DB.prepare(
      `INSERT INTO sources (id, source_type, license_status, can_display_full_text, can_synthesize_from,
       original_url, original_title, original_language, original_published_at, snippet,
       publisher_id, attribution_text, processed, created_at)
       VALUES (?, 'government_api', 'open_government', 1, 1, ?, ?, 'de', ?, ?, ?, ?, 0, ?)`
    ).bind(
      sourceId, url,
      item.Title || item.BusinessShortNumber || 'Parliamentary business',
      item.SubmissionDate || now(),
      (item.Description || item.InitialSituation || '').slice(0, 500),
      'gov-parlament',
      `Schweizer Parlament – ${item.Title || item.BusinessShortNumber || ''}`,
      now()
    ).run();

    await enqueue(env, {
      type: 'process_source',
      payload: { source_id: sourceId },
    });
  }
}

async function ingestOpendataSwiss(env: Env): Promise<void> {
  // CKAN-based open data portal
  const response = await fetch(
    'https://opendata.swiss/api/3/action/recently_changed_packages_activity_list?limit=20',
    { headers: { 'User-Agent': 'Signal.ch/0.1' } }
  );
  if (!response.ok) return;

  const data = await response.json() as any;
  const items = data?.result || [];

  for (const activity of items) {
    const pkg = activity.data?.package;
    if (!pkg) continue;

    const url = `https://opendata.swiss/de/dataset/${pkg.name || pkg.id}`;
    const existing = await env.DB.prepare(
      'SELECT id FROM sources WHERE original_url = ?'
    ).bind(url).first();
    if (existing) continue;

    const sourceId = uuid();
    await env.DB.prepare(
      `INSERT INTO sources (id, source_type, license_status, can_display_full_text, can_synthesize_from,
       original_url, original_title, original_language, original_published_at, snippet,
       publisher_id, attribution_text, processed, created_at)
       VALUES (?, 'government_api', 'open_government', 1, 1, ?, ?, 'de', ?, ?, ?, ?, 0, ?)`
    ).bind(
      sourceId, url,
      pkg.title?.de || pkg.title?.en || pkg.name || 'Dataset update',
      activity.timestamp || now(),
      (pkg.description?.de || pkg.notes || '').slice(0, 500),
      'gov-opendata',
      `opendata.swiss – ${pkg.title?.de || pkg.name || ''}`,
      now()
    ).run();

    await enqueue(env, {
      type: 'process_source',
      payload: { source_id: sourceId },
    });
  }
}

async function ingestSOGC(env: Env): Promise<void> {
  // Swiss Official Gazette of Commerce (SHAB/SOGC)
  const response = await fetch(
    'https://shab.ch/api/v1/publications?pageSize=20&publicationStates=PUBLISHED',
    { headers: { 'User-Agent': 'Signal.ch/0.1' } }
  );
  if (!response.ok) return;

  const data = await response.json() as any;
  const items = data?.content || data?.publications || [];

  for (const item of items) {
    const url = `https://shab.ch/#!/search/publications/detail/${item.id}`;
    const existing = await env.DB.prepare(
      'SELECT id FROM sources WHERE original_url = ?'
    ).bind(url).first();
    if (existing) continue;

    const sourceId = uuid();
    await env.DB.prepare(
      `INSERT INTO sources (id, source_type, license_status, can_display_full_text, can_synthesize_from,
       original_url, original_title, original_language, original_published_at, snippet,
       publisher_id, attribution_text, processed, created_at)
       VALUES (?, 'government_api', 'open_government', 1, 1, ?, ?, 'de', ?, ?, ?, ?, 0, ?)`
    ).bind(
      sourceId, url,
      item.title || item.rubric || 'SHAB publication',
      item.publicationDate || now(),
      (item.message || item.text || '').slice(0, 500),
      'gov-shab',
      `SHAB – ${item.title || item.rubric || ''}`,
      now()
    ).run();

    await enqueue(env, {
      type: 'process_source',
      payload: { source_id: sourceId },
    });
  }
}

async function ingestBFS(env: Env): Promise<void> {
  // Federal Statistical Office (BFS) news
  const response = await fetch(
    'https://www.bfs.admin.ch/bfs/de/home/aktuell/neue-veroeffentlichungen.gnpdetail.html?format=json&pageSize=20',
    { headers: { 'User-Agent': 'Signal.ch/0.1' } }
  );
  if (!response.ok) return;

  const data = await response.json() as any;
  const items = data?.items || data?.results || [];

  for (const item of items) {
    const url = item.url || item.link || `https://www.bfs.admin.ch/id/${item.id}`;
    const existing = await env.DB.prepare(
      'SELECT id FROM sources WHERE original_url = ?'
    ).bind(url).first();
    if (existing) continue;

    const sourceId = uuid();
    await env.DB.prepare(
      `INSERT INTO sources (id, source_type, license_status, can_display_full_text, can_synthesize_from,
       original_url, original_title, original_language, original_published_at, snippet,
       publisher_id, attribution_text, processed, created_at)
       VALUES (?, 'government_api', 'open_government', 1, 1, ?, ?, 'de', ?, ?, ?, ?, 0, ?)`
    ).bind(
      sourceId, url,
      item.title || 'BFS publication',
      item.date || now(),
      (item.lead || item.description || '').slice(0, 500),
      'gov-bfs',
      `BFS – ${item.title || ''}`,
      now()
    ).run();

    await enqueue(env, {
      type: 'process_source',
      payload: { source_id: sourceId },
    });
  }
}

// --- Source Processing ---

async function processSource(payload: Record<string, unknown>, env: Env): Promise<void> {
  const sourceId = payload.source_id as string;
  const source = await env.DB.prepare('SELECT * FROM sources WHERE id = ?').bind(sourceId).first();
  if (!source || source.processed) return;

  // Simple classification based on publisher and title keywords
  const category = classifySource(source);
  const title = source.original_title as string || '';
  const snippet = source.snippet as string || '';

  // Try to match to existing IO or create new one
  let ioId = await findMatchingIO(title, snippet, category, env);

  if (!ioId) {
    // Create new IO
    ioId = uuid();
    await env.DB.prepare(
      `INSERT INTO intelligence_objects (id, status, category, scope, version_count,
       confirmation_density, first_reported_at, created_at, updated_at)
       VALUES (?, 'draft', ?, 'national', 0, 0, ?, ?, ?)`
    ).bind(ioId, category, now(), now(), now()).run();
  }

  // Link source to IO
  await env.DB.prepare(
    `UPDATE sources SET assigned_io_id = ?, processed = 1 WHERE id = ?`
  ).bind(ioId, sourceId).run();

  // Update IO source count and density
  const sourceCount = await env.DB.prepare(
    'SELECT COUNT(*) as c FROM sources WHERE assigned_io_id = ?'
  ).bind(ioId).first();
  const density = Math.min(((sourceCount?.c as number) || 1) / 5, 1);

  await env.DB.prepare(
    `UPDATE intelligence_objects SET confirmation_density = ?, last_source_added_at = ?, updated_at = ? WHERE id = ?`
  ).bind(density, now(), now(), ioId).run();

  // Enqueue synthesis if we have enough sources
  if ((sourceCount?.c as number) >= 2) {
    await enqueue(env, {
      type: 'synthesize_io',
      payload: { io_id: ioId },
    });
  }
}

// --- IO Synthesis ---

async function synthesizeIO(payload: Record<string, unknown>, env: Env): Promise<void> {
  const ioId = payload.io_id as string;
  const io = await env.DB.prepare('SELECT * FROM intelligence_objects WHERE id = ?').bind(ioId).first();
  if (!io) return;

  // Get all sources for this IO
  const sources = await env.DB.prepare(
    'SELECT * FROM sources WHERE assigned_io_id = ? ORDER BY original_published_at DESC'
  ).bind(ioId).all();

  if (sources.results.length === 0) return;

  const sourceSummaries = sources.results.map((s) =>
    `[${s.publisher_id}] ${s.original_title}: ${s.snippet || ''}`
  ).join('\n\n');

  // Synthesize content using Claude API (or template fallback)
  let contentDe: Record<string, unknown>;
  let contentFr: Record<string, unknown> | null = null;

  if (env.ANTHROPIC_API_KEY) {
    contentDe = await synthesizeWithClaude(sourceSummaries, io.category as string, 'de', env);
    contentFr = await synthesizeWithClaude(sourceSummaries, io.category as string, 'fr', env);
  } else {
    contentDe = templateSynthesis(sources.results, io.category as string, 'de');
  }

  // Create new version
  const versionId = uuid();
  const versionNumber = ((io.version_count as number) || 0) + 1;

  await env.DB.prepare(
    `INSERT INTO io_versions (id, io_id, version_number, trigger_type, content_de, content_fr,
     review_status, created_at)
     VALUES (?, ?, ?, 'new_source', ?, ?, 'pending', ?)`
  ).bind(
    versionId, ioId, versionNumber,
    JSON.stringify(contentDe),
    contentFr ? JSON.stringify(contentFr) : null,
    now()
  ).run();

  // Update IO
  await env.DB.prepare(
    `UPDATE intelligence_objects SET version_count = ?, updated_at = ? WHERE id = ?`
  ).bind(versionNumber, now(), ioId).run();
}

async function synthesizeWithClaude(
  sourceSummaries: string,
  category: string,
  language: string,
  env: Env
): Promise<Record<string, unknown>> {
  const langName = { de: 'German', fr: 'French', it: 'Italian', en: 'English' }[language] || 'German';

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2000,
      messages: [{
        role: 'user',
        content: `You are a Swiss news intelligence synthesizer for Signal.ch. Synthesize the following sources into a factual, neutral intelligence object in ${langName}.

Category: ${category}

Sources:
${sourceSummaries}

Respond in JSON with this structure:
{
  "title": "concise factual title",
  "lead": "1-2 sentence summary",
  "summary": "3-4 sentence overview",
  "sections": [
    {"type": "background", "content": "relevant context"},
    {"type": "development", "content": "what happened"},
    {"type": "impact", "content": "significance and implications"}
  ]
}

Rules:
- Use only facts present in the sources
- No opinion or editorial language
- Each sentence must be independently verifiable
- Minimum 10 words per original sentence (no copy-paste from sources)
- Follow Swiss German conventions (ss not ß, Swiss place names)`
      }],
    }),
  });

  const data = await response.json() as any;
  const text = data?.content?.[0]?.text || '{}';

  try {
    return JSON.parse(text);
  } catch {
    // Try extracting JSON from markdown code block
    const match = text.match(/```(?:json)?\s*([\s\S]*?)```/);
    if (match) return JSON.parse(match[1]);
    return templateSynthesis([], category, language);
  }
}

function templateSynthesis(
  sources: Record<string, unknown>[],
  category: string,
  language: string
): Record<string, unknown> {
  const firstSource = sources[0];
  const title = (firstSource?.original_title as string) || 'New development';
  const snippet = (firstSource?.snippet as string) || '';

  return {
    title,
    lead: snippet.slice(0, 200),
    summary: snippet,
    sections: [
      { type: 'development', content: snippet },
    ],
  };
}

// --- Search Index Sync ---

async function syncSearchIndex(payload: Record<string, unknown>, env: Env): Promise<void> {
  const ioId = payload.io_id as string;
  const io = await env.DB.prepare('SELECT * FROM intelligence_objects WHERE id = ?').bind(ioId).first();
  if (!io || io.status !== 'published') return;

  // Get current version content for embedding
  const version = await env.DB.prepare(
    'SELECT * FROM io_versions WHERE id = ?'
  ).bind(io.current_version_id).first();
  if (!version) return;

  const contentDe = JSON.parse((version.content_de as string) || '{}');
  const textForEmbedding = `${contentDe.title || ''} ${contentDe.summary || ''} ${contentDe.lead || ''}`;

  // Generate embedding via Cloudflare Workers AI
  let embedding: number[] | null = null;

  try {
    const result = await env.AI.run('@cf/baai/bge-m3', {
      text: [textForEmbedding],
    }) as { data: number[][] };
    embedding = result.data?.[0] ?? null;
  } catch { /* continue with placeholder */ }

  // Upsert to Vectorize
  await env.VECTORIZE.upsert([{
    id: ioId,
    values: embedding || new Array(1024).fill(0),
    metadata: {
      status: 'published',
      category: io.category as string,
      scope: io.scope as string,
    },
  }]);
}

// --- Helpers ---

function classifySource(source: Record<string, unknown>): string {
  const title = ((source.original_title as string) || '').toLowerCase();
  const publisherId = (source.publisher_id as string) || '';

  if (publisherId.includes('parlament') || title.match(/motion|postulat|interpellation|initiative|abstimmung/))
    return 'politics';
  if (title.match(/budget|steuer|finanz|wirtschaft|bnp|inflation|arbeitslos/))
    return 'economy';
  if (title.match(/gericht|urteil|gesetz|verordnung|recht/))
    return 'legal';
  if (title.match(/bildung|schule|universit|forschung/))
    return 'education';
  if (title.match(/umwelt|klima|energie|verkehr/))
    return 'environment';
  if (title.match(/gesundheit|spital|covid|pandemie/))
    return 'health';
  if (publisherId.includes('bfs'))
    return 'statistics';
  if (publisherId.includes('shab'))
    return 'economy';

  return 'general';
}

async function findMatchingIO(
  title: string,
  snippet: string,
  category: string,
  env: Env
): Promise<string | null> {
  // Simple keyword-based matching against recent draft/published IOs
  const recentIOs = await env.DB.prepare(
    `SELECT io.id, v.content_de FROM intelligence_objects io
     LEFT JOIN io_versions v ON io.current_version_id = v.id
     WHERE io.category = ? AND io.created_at >= datetime('now', '-3 days')
     LIMIT 50`
  ).bind(category).all();

  const titleWords = title.toLowerCase().split(/\s+/).filter(w => w.length > 4);

  for (const io of recentIOs.results) {
    const ioContent = ((io.content_de as string) || '').toLowerCase();
    const matchCount = titleWords.filter(w => ioContent.includes(w)).length;
    if (matchCount >= 3) return io.id as string;
  }

  return null;
}

// --- RSS Parser (minimal) ---

function parseRssItems(xml: string): { title: string; link: string; description: string; pubDate: string }[] {
  const items: { title: string; link: string; description: string; pubDate: string }[] = [];

  // Simple regex-based RSS parsing (Workers don't have DOMParser)
  const itemRegex = /<item>([\s\S]*?)<\/item>/gi;
  let match;

  while ((match = itemRegex.exec(xml)) !== null) {
    const itemXml = match[1];
    items.push({
      title: extractTag(itemXml, 'title'),
      link: extractTag(itemXml, 'link'),
      description: extractTag(itemXml, 'description'),
      pubDate: extractTag(itemXml, 'pubDate'),
    });
  }

  // Also handle Atom feeds
  if (items.length === 0) {
    const entryRegex = /<entry>([\s\S]*?)<\/entry>/gi;
    while ((match = entryRegex.exec(xml)) !== null) {
      const entryXml = match[1];
      const linkMatch = entryXml.match(/<link[^>]*href="([^"]*)"[^>]*\/?>/)
        || entryXml.match(/<link>([^<]*)<\/link>/);
      items.push({
        title: extractTag(entryXml, 'title'),
        link: linkMatch?.[1] || '',
        description: extractTag(entryXml, 'summary') || extractTag(entryXml, 'content'),
        pubDate: extractTag(entryXml, 'published') || extractTag(entryXml, 'updated'),
      });
    }
  }

  return items;
}

function extractTag(xml: string, tag: string): string {
  const match = xml.match(new RegExp(`<${tag}[^>]*><!\\[CDATA\\[([\\s\\S]*?)\\]\\]></${tag}>`, 'i'))
    || xml.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, 'i'));
  return match?.[1]?.trim() || '';
}

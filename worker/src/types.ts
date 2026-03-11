export interface Env {
  DB: D1Database;
  VECTORIZE: VectorizeIndex;
  R2: R2Bucket;
  CACHE: KVNamespace;
  INGESTION_QUEUE: Queue;
  JWT_SECRET: string;
  ANTHROPIC_API_KEY: string;
  COHERE_API_KEY: string;
  APP_ENV: string;
}

export interface IOContent {
  title: string;
  lead: string;
  sections: { type: string; content: string; attributions?: string[] }[];
  summary: string;
  quality_assessment?: {
    confirmation_density: number;
    completeness_score: number;
    missing_elements: string[];
  };
}

export interface Publisher {
  id: string;
  name: string;
  slug: string;
  publisher_type: string;
  media_group: string | null;
  languages: string[];
  reliability_score: number;
  license_type: string | null;
  license_allows_synthesis: boolean;
  license_allows_full_text: boolean;
  rss_feeds: { url: string; language: string; category?: string }[];
  scrape_config: Record<string, unknown>;
}

export interface IntelligenceObject {
  id: string;
  created_at: string;
  updated_at: string;
  status: string;
  category: string;
  subcategory: string | null;
  scope: string;
  canton_codes: string[] | null;
  confirmation_density: number | null;
  source_diversity: number | null;
  completeness_score: number | null;
  bias_spectrum: Record<string, number>;
  missing_elements: string[] | null;
  current_version_id: string | null;
  version_count: number;
  first_reported_at: string | null;
  last_source_added_at: string | null;
}

export interface Source {
  id: string;
  source_type: string;
  license_status: string;
  can_display_full_text: boolean;
  can_synthesize_from: boolean;
  original_url: string;
  original_title: string | null;
  original_language: string | null;
  original_published_at: string | null;
  snippet: string | null;
  publisher_id: string | null;
  attribution_text: string;
  processed: boolean;
  assigned_io_id: string | null;
}

export interface Entity {
  id: string;
  entity_type: string;
  canonical_name: string;
  aliases: string[] | null;
  metadata: Record<string, unknown>;
  wikidata_id: string | null;
  mention_count: number;
  last_mentioned_at: string | null;
}

export interface User {
  id: string;
  email: string | null;
  display_name: string | null;
  preferred_language: string;
  canton: string | null;
  tier: string;
  is_admin: boolean;
  is_editor: boolean;
}

export interface QueueMessage {
  type: 'ingest_rss' | 'ingest_api' | 'process_source' | 'synthesize_io' | 'sync_search';
  payload: Record<string, unknown>;
}

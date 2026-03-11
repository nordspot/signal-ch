-- Signal.ch D1 Schema — Initial Migration
-- All UUIDs stored as TEXT (D1 is SQLite-based)

CREATE TABLE IF NOT EXISTS publishers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  publisher_type TEXT NOT NULL,
  media_group TEXT,
  country TEXT NOT NULL DEFAULT 'CH',
  languages TEXT NOT NULL DEFAULT '["de"]', -- JSON array
  estimated_monthly_reach INTEGER,
  reliability_score REAL NOT NULL DEFAULT 0.5,
  claims_verified_count INTEGER NOT NULL DEFAULT 0,
  claims_contradicted_count INTEGER NOT NULL DEFAULT 0,
  correction_rate REAL,
  license_type TEXT,
  license_expires_at TEXT,
  license_allows_synthesis INTEGER NOT NULL DEFAULT 0,
  license_allows_full_text INTEGER NOT NULL DEFAULT 0,
  political_lean TEXT NOT NULL DEFAULT '{}', -- JSON
  editorial_independence_score REAL,
  rss_feeds TEXT NOT NULL DEFAULT '[]', -- JSON array
  api_endpoint TEXT,
  api_key_encrypted TEXT,
  scrape_config TEXT NOT NULL DEFAULT '{}' -- JSON
);

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  email TEXT UNIQUE,
  password_hash TEXT,
  auth_provider TEXT,
  display_name TEXT,
  preferred_language TEXT NOT NULL DEFAULT 'de',
  canton TEXT,
  commune_bfs_number INTEGER,
  tier TEXT NOT NULL DEFAULT 'free',
  stripe_customer_id TEXT,
  tier_expires_at TEXT,
  interests TEXT NOT NULL DEFAULT '[]', -- JSON
  followed_entities TEXT, -- JSON array of UUIDs
  followed_ios TEXT, -- JSON array of UUIDs
  blind_spot_sensitivity REAL NOT NULL DEFAULT 0.5,
  notification_config TEXT NOT NULL DEFAULT '{}', -- JSON
  reputation_score REAL NOT NULL DEFAULT 0.0,
  verified_expertise TEXT, -- JSON array
  annotation_accuracy REAL,
  data_deletion_requested_at TEXT,
  consent_personalization INTEGER NOT NULL DEFAULT 0,
  consent_analytics INTEGER NOT NULL DEFAULT 0,
  is_admin INTEGER NOT NULL DEFAULT 0,
  is_editor INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS intelligence_objects (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  status TEXT NOT NULL DEFAULT 'draft',
  category TEXT NOT NULL,
  subcategory TEXT,
  scope TEXT NOT NULL DEFAULT 'national',
  canton_codes TEXT, -- JSON array
  commune_bfs_numbers TEXT, -- JSON array
  confirmation_density REAL,
  source_diversity REAL,
  temporal_freshness REAL,
  completeness_score REAL,
  editorial_independence REAL,
  bias_spectrum TEXT NOT NULL DEFAULT '{}', -- JSON
  missing_elements TEXT, -- JSON array
  current_version_id TEXT,
  version_count INTEGER NOT NULL DEFAULT 0,
  first_reported_at TEXT,
  last_source_added_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_io_status ON intelligence_objects(status);
CREATE INDEX IF NOT EXISTS idx_io_category ON intelligence_objects(category);
CREATE INDEX IF NOT EXISTS idx_io_scope ON intelligence_objects(scope);
CREATE INDEX IF NOT EXISTS idx_io_created ON intelligence_objects(created_at);

CREATE TABLE IF NOT EXISTS io_versions (
  id TEXT PRIMARY KEY,
  io_id TEXT NOT NULL REFERENCES intelligence_objects(id) ON DELETE CASCADE,
  version_number INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  content_de TEXT, -- JSON
  content_fr TEXT, -- JSON
  content_it TEXT, -- JSON
  content_en TEXT, -- JSON
  trigger_type TEXT NOT NULL,
  trigger_source_ids TEXT, -- JSON array
  diff_summary TEXT, -- JSON
  reviewed_by TEXT REFERENCES users(id),
  reviewed_at TEXT,
  review_status TEXT NOT NULL DEFAULT 'pending',
  UNIQUE(io_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_iov_io_id ON io_versions(io_id);
CREATE INDEX IF NOT EXISTS idx_iov_review ON io_versions(review_status);

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  source_type TEXT NOT NULL,
  license_status TEXT NOT NULL,
  can_display_full_text INTEGER NOT NULL DEFAULT 0,
  can_synthesize_from INTEGER NOT NULL DEFAULT 0,
  requires_link_back INTEGER NOT NULL DEFAULT 1,
  original_url TEXT NOT NULL,
  original_title TEXT,
  original_language TEXT,
  original_published_at TEXT,
  full_text_encrypted TEXT,
  snippet TEXT,
  publisher_id TEXT REFERENCES publishers(id),
  attribution_text TEXT NOT NULL,
  author_name TEXT,
  publisher_reliability_score REAL,
  processed INTEGER NOT NULL DEFAULT 0,
  assigned_io_id TEXT REFERENCES intelligence_objects(id),
  extracted_entities TEXT NOT NULL DEFAULT '[]' -- JSON
);

CREATE INDEX IF NOT EXISTS idx_sources_publisher ON sources(publisher_id);
CREATE INDEX IF NOT EXISTS idx_sources_processed ON sources(processed) WHERE processed = 0;
CREATE INDEX IF NOT EXISTS idx_sources_url ON sources(original_url);

CREATE TABLE IF NOT EXISTS entities (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  entity_type TEXT NOT NULL,
  canonical_name TEXT NOT NULL,
  names_de TEXT, -- JSON array
  names_fr TEXT, -- JSON array
  names_it TEXT, -- JSON array
  names_en TEXT, -- JSON array
  aliases TEXT, -- JSON array
  metadata TEXT NOT NULL DEFAULT '{}', -- JSON
  wikidata_id TEXT,
  lobbywatch_id TEXT,
  sogc_uid TEXT,
  bfs_number INTEGER,
  mention_count INTEGER NOT NULL DEFAULT 0,
  last_mentioned_at TEXT,
  coi_data TEXT NOT NULL DEFAULT '{}' -- JSON
);

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(canonical_name);
CREATE INDEX IF NOT EXISTS idx_entities_wikidata ON entities(wikidata_id) WHERE wikidata_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS entity_relations (
  id TEXT PRIMARY KEY,
  source_entity_id TEXT NOT NULL REFERENCES entities(id),
  target_entity_id TEXT NOT NULL REFERENCES entities(id),
  relation_type TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.5,
  source_io_ids TEXT, -- JSON array
  valid_from TEXT,
  valid_to TEXT,
  metadata TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_er_source ON entity_relations(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_er_target ON entity_relations(target_entity_id);

CREATE TABLE IF NOT EXISTS io_sources (
  io_id TEXT NOT NULL REFERENCES intelligence_objects(id),
  source_id TEXT NOT NULL REFERENCES sources(id),
  added_at TEXT NOT NULL DEFAULT (datetime('now')),
  relevance_score REAL NOT NULL DEFAULT 0.5,
  contribution_type TEXT NOT NULL,
  PRIMARY KEY (io_id, source_id)
);

CREATE TABLE IF NOT EXISTS io_entities (
  io_id TEXT NOT NULL REFERENCES intelligence_objects(id),
  entity_id TEXT NOT NULL REFERENCES entities(id),
  role TEXT,
  sentiment REAL,
  mention_count INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (io_id, entity_id)
);

CREATE TABLE IF NOT EXISTS user_io_interactions (
  user_id TEXT NOT NULL REFERENCES users(id),
  io_id TEXT NOT NULL REFERENCES intelligence_objects(id),
  first_read_version_id TEXT,
  first_read_at TEXT,
  last_read_version_id TEXT,
  last_read_at TEXT,
  shared_version_id TEXT,
  shared_at TEXT,
  shared_via TEXT,
  reading_time_seconds INTEGER,
  scroll_depth REAL,
  bookmarked INTEGER NOT NULL DEFAULT 0,
  clipped_to_mindmap INTEGER NOT NULL DEFAULT 0,
  notified_of_update INTEGER NOT NULL DEFAULT 0,
  notified_at TEXT,
  PRIMARY KEY (user_id, io_id)
);

CREATE TABLE IF NOT EXISTS annotations (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  io_id TEXT NOT NULL REFERENCES intelligence_objects(id),
  io_version_id TEXT NOT NULL REFERENCES io_versions(id),
  annotation_level TEXT NOT NULL,
  target_selector TEXT, -- JSON
  annotation_type TEXT NOT NULL,
  author_id TEXT NOT NULL REFERENCES users(id),
  body TEXT NOT NULL,
  evidence_urls TEXT, -- JSON array
  useful_votes INTEGER NOT NULL DEFAULT 0,
  not_useful_votes INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active',
  moderation_reason TEXT,
  fact_check_verdict TEXT
);

CREATE INDEX IF NOT EXISTS idx_annotations_io ON annotations(io_id);

CREATE TABLE IF NOT EXISTS votes_and_initiatives (
  id TEXT PRIMARY KEY,
  vote_type TEXT NOT NULL,
  level TEXT NOT NULL,
  canton TEXT,
  commune_bfs_number INTEGER,
  title_de TEXT,
  title_fr TEXT,
  title_it TEXT,
  official_url TEXT,
  vote_date TEXT,
  status TEXT NOT NULL,
  result TEXT, -- JSON
  synthesized_io_id TEXT,
  pro_arguments TEXT, -- JSON
  contra_arguments TEXT, -- JSON
  financial_impact TEXT, -- JSON
  historical_precedents TEXT, -- JSON array
  curia_vista_id TEXT
);

CREATE TABLE IF NOT EXISTS agency_publications (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  agency_id TEXT NOT NULL REFERENCES publishers(id),
  title_de TEXT,
  title_fr TEXT,
  title_it TEXT,
  original_url TEXT NOT NULL,
  publication_date TEXT,
  publication_type TEXT,
  raw_content_path TEXT,
  synthesized_io_id TEXT,
  synthesis_status TEXT NOT NULL DEFAULT 'pending',
  views_count INTEGER NOT NULL DEFAULT 0,
  unique_readers INTEGER NOT NULL DEFAULT 0,
  avg_reading_time_seconds REAL,
  shares_count INTEGER NOT NULL DEFAULT 0
);

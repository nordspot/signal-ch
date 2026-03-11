# CLAUDE.md — SIGNAL.CH MASTER PROMPT
# The Swiss Intelligence Layer for News
# Nord · Ittigen, Switzerland · March 2026
# Version 1.0 — CONFIDENTIAL

---

## TABLE OF CONTENTS

1. PROJECT IDENTITY & VISION
2. STRATEGIC CONTEXT
3. LEGAL FRAMEWORK & CONSTRAINTS
4. ARCHITECTURE OVERVIEW
5. TECH STACK & INFRASTRUCTURE
6. DATABASE SCHEMA & DATA MODELS
7. INGESTION ENGINE (THE CRAWLER)
8. SYNTHESIS ENGINE (THE BRAIN)
9. KNOWLEDGE GRAPH (THE MEMORY)
10. API LAYER
11. FRONTEND APPLICATION
12. AI PODCAST & MEDIA GENERATION
13. USER SYSTEM & PERSONALIZATION
14. COMMENT & ANNOTATION SYSTEM
15. DEMOCRACY TOOLKIT
16. SEARCH & CONVERSATIONAL AI
17. NOTIFICATION INTELLIGENCE
18. ADVERTISING ENGINE
19. GOVERNMENT AGENCY B2G PORTAL
20. ADMIN & EDITORIAL DASHBOARD
21. MONITORING, HEALTH & SELF-HEALING
22. DEPLOYMENT & DEVOPS
23. PHASE ROADMAP & BUILD ORDER
24. CODING CONVENTIONS & INVARIANTS
25. OPEN QUESTIONS & KNOWN RISKS

---

## 1. PROJECT IDENTITY & VISION

### What Is Signal.ch?

Signal.ch is an AI-native news intelligence platform for Switzerland. It does NOT aggregate
news — it SYNTHESIZES it. Every news event becomes a living "Intelligence Object" (IO) that
evolves as new sources confirm, contradict, or add nuance. Every article carries transparent
DNA: provenance, confidence, bias spectrum, and completeness score.

### The Core Promise

"Signal.ch makes you the most informed person in any room about Switzerland — in 10 minutes a day."

### Product Name

SIGNAL.CH — "The Intelligence Layer for Swiss News"

Domain targets: signal.ch (primary), signal.swiss (backup), getsignal.ch (fallback)
Trademark: File with IPI (Swiss Federal Institute of Intellectual Property)

### Who Builds This

Nord (nord.spot) — Swiss AI agency based in Ittigen. Co-founders Daniel and Stefan Brauchli.
Sub-brand architecture: Signal.ch orbits Nord in the "Orrery" brand system alongside CRUNCH,
airtime, PodCam, and Vivo Vault.

Signal.ch will be incorporated as a separate legal entity (GmbH initially, convert to AG for
fundraising) to isolate liability from Nord's other operations.

### Strategic Partnership

Nau.ch (Nau media AG) — Switzerland's #4 news portal with 4M monthly unique clients, 70
employees, 128 Gemeindeseiten (local community pages), existing Keystone-SDA licensing
relationships, and recent CHF 7.5M fundraise. They lost their Livesystems DOOH screen
distribution to Ringier in Jan 2026 and need a new strategic edge.

The pitch: Signal.ch is nau.ch's AI layer. We bring the technology, they bring the audience,
editorial credibility, and content licensing umbrella.

### Government Agency Partners

Through existing Nord relationships with BFS (Bundesamt für Statistik) and BFU
(Beratungsstelle für Unfallverhütung), we position federal agencies as Signal.ch's first
PAYING CUSTOMERS. They spend millions producing reports nobody reads. We solve their
distribution problem and get premium content for free (or they pay us).

---

## 2. STRATEGIC CONTEXT

### Market

- Switzerland: 8.9M population, 4 national languages (DE/FR/IT/RM)
- Highest digital literacy + purchasing power in Europe
- Proven willingness to pay for quality news (NZZ, Republik)
- Media consolidating: TX Group, CH Media, Ringier dominate
- Federal/cantonal/communal structure creates hyperlocal news silos
- Direct democracy requires informed citizens (Abstimmungen, Gemeindeversammlungen)

### Revenue Model (Blended)

| Tier | Price | Description |
|------|-------|-------------|
| Signal Free | CHF 0 | 5 IOs/day, basic brief, ad-supported |
| Signal Personal | CHF 19/mo | Unlimited IOs, full briefs, audio, no ads |
| Signal Pro | CHF 49/mo | + conversational search, mind maps, entity profiles, API |
| Signal Enterprise | CHF 99/mo/seat | + team workspaces, dashboards, webhooks, bulk API |
| B2G Agency | CHF 2-5K/mo | Distribution + analytics for government publications |

### Phase Roadmap (Summary — detail in §23)

- Phase 0 (Mo 1-3): Government data layer only. Zero licensing cost. Legal. Production-ready.
- Phase 1 (Mo 3-6): Nau.ch partnership. First 10K users. Referral-based content integration.
- Phase 2 (Mo 6-12): Freemium launch. First revenue. First licenses (Keystone-SDA).
- Phase 3 (Mo 12-18): Full feature set. Wire services. 50K users. Enterprise tier.
- Phase 4 (Mo 18-24): 100K subscribers. Full licensing. Break-even at ~Month 20.

---

## 3. LEGAL FRAMEWORK & CONSTRAINTS

### CRITICAL: Read This Before Writing Any Ingestion Code

Swiss copyright law (URG/CopA) protects EXPRESSION, not FACTS. Our entire model depends on
this distinction being architecturally enforced.

### What We CAN Do (Green Zone)

1. Government sources: admin.ch, Curia Vista, SOGC/SHAB, courts, BFS, cantonal data — ALL
   public domain or open data. This is our Phase 0 foundation.
2. Press releases: Companies WANT distribution. Wire services (BusinessWire, GlobeNewswire)
   are free raw material.
3. Quotation right (Art. 25 CopA): We may quote SHORT excerpts from published works WITH
   source citation and author credit, as long as the quotation serves our original work.
4. Current events reporting (Art. 28 CopA): As a news organization, we may reproduce works
   "to the extent required by the purpose of reporting."
5. Facts & data: Stock prices, election results, sports scores, who-what-when-where, patent
   filings (Art. 5 CopA explicitly excludes patents from copyright).
6. RSS feed monitoring: Headlines + snippets + URLs from published RSS feeds. Publishers
   intentionally make these machine-readable.
7. Social media embeds: Official embed APIs (Twitter, YouTube, Instagram) are designed for
   third-party display.
8. opendata.swiss: 14,279 datasets from 65+ organizations via CKAN API. Free. Legal.

### What We CANNOT Do (Red Zone)

1. Reproduce full article text or close paraphrasing from copyrighted sources
2. Download/store copyrighted images without a license
3. Scrape behind paywalls (Art. 39a CopA: circumventing technical protection = criminal)
4. Use copyrighted content to fine-tune our own models
5. Feed copyrighted photos into image-to-image AI pipelines
6. Publish AI-generated content that closely mirrors the structure of copyrighted articles

### Gray Zone (Defensible But Careful)

1. AI synthesis from extracted facts across multiple sources — ENSURE the synthesis is
   genuinely original expression, not cosmetic rewriting
2. Transient copies during processing — unlitigated in CH, but defensible
3. RSS + headline clustering without touching full articles

### Incoming Legislation

- **Leistungsschutzrecht (Ancillary Copyright)**: Swiss Federal Council actively preparing
  legislation. Large online services reaching 10%+ of Swiss population must pay media
  companies for snippets. National Council committee rejected current bill (Oct 2025, 18-3)
  demanding AI use also be regulated. Next version will be BROADER.
- **Motion Gössi**: Demands explicit rights-holder permission for AI training. Adopted by
  Council of States March 2025.
- **Platform Act**: Under consultation (deadline Feb 2026). Targets very large platforms.
  Unlikely to affect us initially but watch at scale.

### Architectural Enforcement

```
EVERY content item in the system MUST carry:
- source_type: enum(GOVERNMENT, PRESS_RELEASE, WIRE_SERVICE, LICENSED_MEDIA,
                     RSS_METADATA, SOCIAL_EMBED, CITIZEN, OPEN_DATA, SYNTHESIZED)
- license_status: enum(PUBLIC_DOMAIN, OPEN_LICENSE, LICENSED, FAIR_USE_QUOTATION,
                        RSS_METADATA_ONLY, PENDING_LICENSE, UNLICENSED)
- can_display_full_text: boolean
- can_synthesize_from: boolean
- requires_link_back: boolean
- attribution_text: string
- original_url: string (always populated — we ALWAYS link back)
```

The ingestion engine MUST enforce license_status checks before ANY content enters the
synthesis pipeline. UNLICENSED content may only be used for: event detection, entity
extraction from metadata, topic clustering from headlines. Never for text synthesis.

### Data Protection (nDSG/FADP)

- Privacy by Design & Default (Art. 7 FADP) — baked in from day one
- DPIA required for: personalized briefs, sentiment analysis, entity profiling, ad targeting
- Breach notification to FDPIC for high-risk breaches — reading habits = political preferences = sensitive
- Penalties: Up to CHF 250,000 against INDIVIDUALS (not company). Personal risk for founders.
- Google consent policy: If using Google Ads, need certified CMP with TCF support
- Our contextual ad model = compliance advantage (less personal data processing)

### Editorial Responsibility

Signal.ch bears liability for ALL published content, including AI-generated synthesis:
- Defamation (Art. 173-178 StGB)
- Personality rights (Art. 28 ZGB)
- Unfair competition (UWG)

REQUIREMENT: Human editorial review on all AI synthesis before publication, at minimum during
Phase 0-2. The system MUST have an editorial review queue with approve/reject/edit workflow.

---

## 4. ARCHITECTURE OVERVIEW

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SIGNAL.CH PLATFORM                           │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ INGESTION│  │SYNTHESIS │  │KNOWLEDGE │  │  DELIVERY LAYER   │   │
│  │ ENGINE   │──│ ENGINE   │──│ GRAPH    │──│ (Web/App/API/     │   │
│  │ (Crawler)│  │ (Brain)  │  │ (Memory) │  │  Podcast/Video)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────────────┘   │
│       │              │              │                                │
│  ┌────┴──────────────┴──────────────┴──────────────────────────┐   │
│  │                    DATA LAYER                                │   │
│  │  PostgreSQL + pgvector (NORDB) │ Redis │ S3-compatible      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    LLM ROUTING (SPOT 3-Lane)                 │   │
│  │  Lane 1: Local Llama 3.x (classification, NER, triage)      │   │
│  │  Lane 2: Local RAG (knowledge graph queries, embeddings)     │   │
│  │  Lane 3: Claude API (synthesis, complex analysis, search)    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Design Principles

1. **Swiss Data Sovereignty**: All user data and Swiss-sourced content stored on Swiss soil.
   Primary: Infomaniak (CH). Backup: Hetzner (DE). LLM API calls via DPA that prevents
   training on our data.
2. **Intelligence Objects, Not Articles**: The IO is the atomic unit. Not a page, not an
   article — a living knowledge entity with versions, sources, entities, and scores.
3. **Source Transparency by Default**: Every sentence traceable to source(s). Every IO shows
   its provenance chain. Nothing is opaque.
4. **Multilingual Native**: DE/FR/IT/EN are first-class citizens. Not translated afterthoughts.
   Each language version synthesized from sources IN that language, enriched with cross-
   language facts.
5. **License Compliance as Architecture**: The system CANNOT accidentally publish unlicensed
   content. Legal constraints are enforced in code, not policy.

---

## 5. TECH STACK & INFRASTRUCTURE

### Backend

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Primary API | Python 3.12+ (FastAPI) | ML ecosystem, async, type hints |
| Task Queue | Celery + Redis | Distributed scraping, synthesis jobs |
| Database | PostgreSQL 16 + pgvector | Relational + vector search in one DB |
| Vector Store | pgvector (primary), Qdrant (if pgvector perf insufficient) | Semantic search |
| Cache | Redis | Session, rate limiting, real-time feeds |
| Object Storage | S3-compatible (Infomaniak or MinIO) | Media, PDFs, audio files |
| Search | Meilisearch | Instant full-text search (Swiss language support) |
| Real-time | WebSockets (via FastAPI) | Live updates, collaborative annotations |
| Message Bus | Redis Streams or NATS | Inter-service communication |

### Frontend

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Web App | Next.js 14+ (App Router) | SSR, i18n, performance |
| Mobile | React Native or Capacitor | Cross-platform from web codebase |
| State | Zustand or Jotai | Lightweight, no boilerplate |
| Styling | Tailwind CSS | Utility-first, design system friendly |
| Maps | MapLibre GL | OSS, Swiss topo maps integration |
| Charts | Recharts or D3 | Data visualizations, entity graphs |
| Rich Text | TipTap (ProseMirror) | Annotation overlay system |

### AI/ML

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Synthesis | Claude API (Opus for complex, Sonnet for routine) | Best multilingual quality |
| Classification | Local Llama 3.2 3B (via Ollama) | Fast, private, free |
| NER (Swiss) | Fine-tuned spaCy or custom model | Swiss German names, political entities |
| Embeddings | Cohere multilingual embed v3 or BGE-M3 | Cross-lingual semantic search |
| Translation | NLLB-200 (local) for bulk, Claude for editorial | Cost vs quality tradeoff |
| TTS | Eleven Labs API or XTTS v2 (local) | Podcast generation |
| STT | Whisper large-v3 (local) | Voice search, audio transcription |
| Image Gen | SDXL (local) for generic illustrations | Not for news photos (licensed) |

### Infrastructure

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Primary Hosting | Infomaniak Public Cloud (CH) | Swiss data sovereignty |
| Backup/Overflow | Hetzner Cloud (DE) | Cost-effective GPU for ML |
| CI/CD | GitHub Actions | Standard, integrates with everything |
| Container Runtime | Docker + Docker Compose (dev), K3s (prod) | Lightweight Kubernetes |
| Reverse Proxy | Caddy or Traefik | Auto TLS, simple config |
| DNS/CDN | Cloudflare (Swiss edge PoPs) | DDoS protection, caching |
| Monitoring | Grafana + Prometheus + Loki | Full observability stack |
| Error Tracking | Sentry (self-hosted) | Swiss-hosted error reporting |

### Hardware (Initial)

- 1x App Server: 8 vCPU, 32GB RAM, 500GB NVMe (Infomaniak)
- 1x DB Server: 8 vCPU, 64GB RAM, 1TB NVMe (PostgreSQL + pgvector)
- 1x ML Server: GPU-equipped (Hetzner GEX44 or similar) for local models
- 1x Redis: 4 vCPU, 16GB RAM
- Estimated monthly: CHF 400-600

Scale plan: Horizontal scaling via K3s. DB read replicas when needed. Separate ML cluster.

---

## 6. DATABASE SCHEMA & DATA MODELS

### Core Tables

```sql
-- ═══════════════════════════════════════════════════════════════
-- INTELLIGENCE OBJECTS (The Atomic Unit)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE intelligence_objects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  -- Current state
  status TEXT NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'review', 'published', 'archived', 'retracted')),
  
  -- Classification
  category TEXT NOT NULL
    CHECK (category IN ('politics', 'economy', 'society', 'culture', 'science',
                         'sport', 'environment', 'health', 'education', 'technology',
                         'legal', 'infrastructure', 'international', 'local', 'opinion')),
  subcategory TEXT,
  
  -- Geographic scope
  scope TEXT NOT NULL DEFAULT 'national'
    CHECK (scope IN ('international', 'national', 'cantonal', 'regional', 'communal')),
  canton_codes TEXT[], -- e.g., {'BE', 'ZH'}
  commune_bfs_numbers INTEGER[], -- BFS commune numbers
  
  -- Quality indicators (computed, updated on each version)
  confirmation_density FLOAT, -- 0-1: how many independent sources confirm
  source_diversity FLOAT, -- 0-1: are sources from different media groups?
  temporal_freshness FLOAT, -- 0-1: how recent are contributing sources?
  completeness_score FLOAT, -- 0-1: AI assessment of unanswered questions
  editorial_independence FLOAT, -- 0-1: independence of contributing sources
  
  -- Bias spectrum (JSON: distribution, not a single label)
  bias_spectrum JSONB NOT NULL DEFAULT '{}',
  -- e.g., {"left_progressive": 0.15, "center": 0.55, "right_conservative": 0.30}
  
  -- Missing elements (AI-identified gaps)
  missing_elements TEXT[],
  -- e.g., {'Official FINMA statement', 'Independent expert analysis'}
  
  -- Versioning
  current_version_id UUID, -- FK to io_versions
  version_count INTEGER NOT NULL DEFAULT 0,
  
  -- Search
  embedding vector(1024), -- multilingual embedding of current synthesis
  
  -- Timestamps
  first_reported_at TIMESTAMPTZ, -- when the event first appeared in any source
  last_source_added_at TIMESTAMPTZ
);

CREATE INDEX idx_io_embedding ON intelligence_objects
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_io_status ON intelligence_objects (status);
CREATE INDEX idx_io_category ON intelligence_objects (category);
CREATE INDEX idx_io_scope ON intelligence_objects (scope);
CREATE INDEX idx_io_cantons ON intelligence_objects USING GIN (canton_codes);
CREATE INDEX idx_io_created ON intelligence_objects (created_at DESC);
CREATE INDEX idx_io_freshness ON intelligence_objects (temporal_freshness DESC);


-- ═══════════════════════════════════════════════════════════════
-- IO VERSIONS (Living Timeline)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE io_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  io_id UUID NOT NULL REFERENCES intelligence_objects(id) ON DELETE CASCADE,
  version_number INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  -- The synthesized content (one per language)
  -- Stored as structured JSON, not flat text
  content_de JSONB, -- {"title": "", "lead": "", "sections": [...], "summary": ""}
  content_fr JSONB,
  content_it JSONB,
  content_en JSONB,
  
  -- What triggered this version
  trigger_type TEXT NOT NULL
    CHECK (trigger_type IN ('initial', 'new_source', 'correction', 'update',
                             'editorial_edit', 'retraction', 'enrichment')),
  trigger_source_ids UUID[], -- which source(s) triggered this version
  
  -- Diff from previous version (structured)
  diff_summary JSONB, -- AI-generated summary of what changed
  
  -- Editorial
  reviewed_by UUID REFERENCES users(id),
  reviewed_at TIMESTAMPTZ,
  review_status TEXT DEFAULT 'pending'
    CHECK (review_status IN ('pending', 'approved', 'rejected', 'auto_approved')),
  
  UNIQUE(io_id, version_number)
);


-- ═══════════════════════════════════════════════════════════════
-- SOURCES (Every Piece of Input)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  -- Origin
  source_type TEXT NOT NULL
    CHECK (source_type IN ('government', 'press_release', 'wire_service',
                            'licensed_media', 'rss_metadata', 'social_embed',
                            'citizen', 'open_data', 'academic', 'corporate')),
  
  -- License & legal status
  license_status TEXT NOT NULL
    CHECK (license_status IN ('public_domain', 'open_license', 'licensed',
                               'fair_use_quotation', 'rss_metadata_only',
                               'pending_license', 'unlicensed')),
  can_display_full_text BOOLEAN NOT NULL DEFAULT false,
  can_synthesize_from BOOLEAN NOT NULL DEFAULT false,
  requires_link_back BOOLEAN NOT NULL DEFAULT true,
  
  -- Content
  original_url TEXT NOT NULL,
  original_title TEXT,
  original_language TEXT CHECK (original_language IN ('de', 'fr', 'it', 'en', 'rm', 'other')),
  original_published_at TIMESTAMPTZ,
  
  -- For licensed/full-text sources only (encrypted at rest)
  full_text_encrypted TEXT,
  
  -- For RSS/metadata-only sources
  snippet TEXT, -- first 2-3 sentences from RSS
  
  -- Attribution (ALWAYS populated)
  publisher_id UUID REFERENCES publishers(id),
  attribution_text TEXT NOT NULL,
  author_name TEXT,
  
  -- Reliability tracking
  publisher_reliability_score FLOAT, -- inherited from publisher, updated over time
  
  -- Processing state
  processed BOOLEAN NOT NULL DEFAULT false,
  assigned_io_id UUID REFERENCES intelligence_objects(id),
  
  -- Embedding for clustering/dedup
  embedding vector(1024),
  
  -- Extracted entities (post-processing)
  extracted_entities JSONB DEFAULT '[]'
);

CREATE INDEX idx_sources_type ON sources (source_type);
CREATE INDEX idx_sources_license ON sources (license_status);
CREATE INDEX idx_sources_publisher ON sources (publisher_id);
CREATE INDEX idx_sources_published ON sources (original_published_at DESC);
CREATE INDEX idx_sources_embedding ON sources
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 200);
CREATE INDEX idx_sources_unprocessed ON sources (processed) WHERE processed = false;


-- ═══════════════════════════════════════════════════════════════
-- PUBLISHERS (Source Reputation System)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE publishers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  
  -- Classification
  publisher_type TEXT NOT NULL
    CHECK (publisher_type IN ('wire_service', 'national_media', 'regional_media',
                               'local_media', 'public_broadcaster', 'government_agency',
                               'academic', 'corporate', 'ngo', 'blog', 'social_platform',
                               'citizen')),
  media_group TEXT, -- e.g., 'TX Group', 'CH Media', 'Ringier', 'SRG SSR'
  
  -- Reach & reliability
  country TEXT NOT NULL DEFAULT 'CH',
  languages TEXT[] NOT NULL, -- ['de', 'fr'] etc.
  estimated_monthly_reach INTEGER,
  reliability_score FLOAT NOT NULL DEFAULT 0.5, -- 0-1, computed over time
  claims_verified_count INTEGER NOT NULL DEFAULT 0,
  claims_contradicted_count INTEGER NOT NULL DEFAULT 0,
  correction_rate FLOAT, -- how often they issue corrections
  
  -- Licensing
  license_type TEXT
    CHECK (license_type IN ('wire_subscription', 'bilateral_license', 'collective_license',
                             'public_domain', 'rss_only', 'partnership', 'none')),
  license_expires_at DATE,
  license_allows_synthesis BOOLEAN NOT NULL DEFAULT false,
  license_allows_full_text BOOLEAN NOT NULL DEFAULT false,
  
  -- Bias assessment (AI-computed, regularly updated)
  political_lean JSONB DEFAULT '{}',
  editorial_independence_score FLOAT,
  
  -- RSS/API endpoints
  rss_feeds JSONB DEFAULT '[]', -- [{"url": "...", "language": "de", "category": "..."}]
  api_endpoint TEXT,
  api_key_encrypted TEXT,
  
  -- Scraping config
  scrape_config JSONB DEFAULT '{}'
  -- {"enabled": true, "interval_minutes": 15, "respect_robots_txt": true,
  --  "max_requests_per_hour": 60, "css_selectors": {...}}
);


-- ═══════════════════════════════════════════════════════════════
-- ENTITIES (Knowledge Graph Nodes)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE entities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  -- Classification
  entity_type TEXT NOT NULL
    CHECK (entity_type IN ('person', 'organization', 'location', 'law',
                            'financial_figure', 'concept', 'event', 'product',
                            'political_party', 'government_body', 'company',
                            'ngo', 'academic_institution')),
  
  -- Names (multilingual, including aliases)
  canonical_name TEXT NOT NULL,
  names_de TEXT[],
  names_fr TEXT[],
  names_it TEXT[],
  names_en TEXT[],
  aliases TEXT[], -- all known alternate names
  
  -- Structured data (type-specific)
  metadata JSONB NOT NULL DEFAULT '{}',
  -- For person: {"birth_date": "", "party": "", "canton": "", "role": "", "lobbywatch_id": ""}
  -- For company: {"uid": "CHE-...", "sogc_id": "", "industry": "", "hq_canton": ""}
  -- For law: {"sr_number": "", "status": "", "effective_date": ""}
  -- For location: {"bfs_number": 0, "canton": "", "coordinates": [lat, lon]}
  
  -- External identifiers
  wikidata_id TEXT,
  lobbywatch_id TEXT,
  sogc_uid TEXT, -- Swiss company UID (CHE-xxx.xxx.xxx)
  bfs_number INTEGER, -- for communes
  
  -- Knowledge graph
  embedding vector(1024),
  mention_count INTEGER NOT NULL DEFAULT 0,
  last_mentioned_at TIMESTAMPTZ,
  
  -- Conflict of interest data (auto-enriched)
  -- For politicians: voting records, donor connections, financial interests
  -- For companies: litigation, SOGC filings, market data
  coi_data JSONB DEFAULT '{}'
);

CREATE INDEX idx_entities_type ON entities (entity_type);
CREATE INDEX idx_entities_name ON entities USING GIN (to_tsvector('simple', canonical_name));
CREATE INDEX idx_entities_embedding ON entities
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_entities_wikidata ON entities (wikidata_id) WHERE wikidata_id IS NOT NULL;
CREATE INDEX idx_entities_sogc ON entities (sogc_uid) WHERE sogc_uid IS NOT NULL;


-- ═══════════════════════════════════════════════════════════════
-- ENTITY RELATIONS (Knowledge Graph Edges)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE entity_relations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_entity_id UUID NOT NULL REFERENCES entities(id),
  target_entity_id UUID NOT NULL REFERENCES entities(id),
  relation_type TEXT NOT NULL
    CHECK (relation_type IN ('works_for', 'member_of', 'subsidiary_of', 'located_in',
                              'regulates', 'opposes', 'supports', 'related_to',
                              'succeeded_by', 'preceded_by', 'funded_by', 'spouse_of',
                              'colleague_of', 'competitor_of', 'parent_org_of')),
  confidence FLOAT NOT NULL DEFAULT 0.5,
  source_io_ids UUID[], -- IOs where this relation was detected
  valid_from DATE,
  valid_to DATE, -- NULL = still active
  metadata JSONB DEFAULT '{}'
);


-- ═══════════════════════════════════════════════════════════════
-- IO-SOURCE MAPPING (Which sources feed which IO)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE io_sources (
  io_id UUID NOT NULL REFERENCES intelligence_objects(id),
  source_id UUID NOT NULL REFERENCES sources(id),
  added_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  relevance_score FLOAT NOT NULL DEFAULT 0.5,
  contribution_type TEXT NOT NULL
    CHECK (contribution_type IN ('confirms', 'adds_detail', 'contradicts',
                                  'provides_context', 'primary_source')),
  PRIMARY KEY (io_id, source_id)
);


-- ═══════════════════════════════════════════════════════════════
-- IO-ENTITY MAPPING (Which entities appear in which IO)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE io_entities (
  io_id UUID NOT NULL REFERENCES intelligence_objects(id),
  entity_id UUID NOT NULL REFERENCES entities(id),
  role TEXT, -- 'subject', 'mentioned', 'affected', 'decision_maker'
  sentiment FLOAT, -- -1 to 1: how the IO portrays this entity
  mention_count INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (io_id, entity_id)
);


-- ═══════════════════════════════════════════════════════════════
-- USERS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  -- Auth (Supabase Auth or similar)
  email TEXT UNIQUE,
  auth_provider TEXT, -- 'email', 'google', 'apple', 'swiss_id'
  
  -- Profile
  display_name TEXT,
  preferred_language TEXT NOT NULL DEFAULT 'de'
    CHECK (preferred_language IN ('de', 'fr', 'it', 'en')),
  
  -- Location (for local content)
  canton TEXT,
  commune_bfs_number INTEGER,
  coordinates POINT, -- optional, for proximity alerts
  
  -- Subscription
  tier TEXT NOT NULL DEFAULT 'free'
    CHECK (tier IN ('free', 'personal', 'pro', 'enterprise')),
  stripe_customer_id TEXT,
  tier_expires_at TIMESTAMPTZ,
  
  -- Personalization (GDPR-compliant, user-controlled)
  interests JSONB DEFAULT '[]', -- topic categories
  followed_entities UUID[], -- entity IDs
  followed_ios UUID[], -- IO IDs actively following
  blind_spot_sensitivity FLOAT DEFAULT 0.5, -- 0=none, 1=aggressive
  
  -- Notification preferences
  notification_config JSONB DEFAULT '{}',
  -- {"morning_brief": true, "morning_time": "07:15", "evening_digest": true,
  --  "breaking_threshold": "high", "commute_mode": true, "audio_preferred": false}
  
  -- Reputation (for annotation/comment system)
  reputation_score FLOAT NOT NULL DEFAULT 0.0,
  verified_expertise TEXT[], -- e.g., ['constitutional_law', 'banking', 'environmental_science']
  annotation_accuracy FLOAT, -- computed from community feedback
  
  -- Privacy
  data_deletion_requested_at TIMESTAMPTZ,
  consent_personalization BOOLEAN NOT NULL DEFAULT false,
  consent_analytics BOOLEAN NOT NULL DEFAULT false
);


-- ═══════════════════════════════════════════════════════════════
-- USER IO INTERACTIONS (Reading History + Version Tracking)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE user_io_interactions (
  user_id UUID NOT NULL REFERENCES users(id),
  io_id UUID NOT NULL REFERENCES intelligence_objects(id),
  
  -- Version tracking (CRITICAL: know which version user read/shared)
  first_read_version_id UUID REFERENCES io_versions(id),
  first_read_at TIMESTAMPTZ,
  last_read_version_id UUID REFERENCES io_versions(id),
  last_read_at TIMESTAMPTZ,
  
  -- Sharing
  shared_version_id UUID REFERENCES io_versions(id),
  shared_at TIMESTAMPTZ,
  shared_via TEXT, -- 'link', 'email', 'whatsapp', 'twitter', etc.
  
  -- Engagement
  reading_time_seconds INTEGER,
  scroll_depth FLOAT, -- 0-1
  bookmarked BOOLEAN NOT NULL DEFAULT false,
  clipped_to_mindmap BOOLEAN NOT NULL DEFAULT false,
  
  -- Update notification
  notified_of_update BOOLEAN NOT NULL DEFAULT false,
  notified_at TIMESTAMPTZ,
  
  PRIMARY KEY (user_id, io_id)
);


-- ═══════════════════════════════════════════════════════════════
-- ANNOTATIONS (Word/Sentence/Paragraph/Article Level)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE annotations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  -- Target
  io_id UUID NOT NULL REFERENCES intelligence_objects(id),
  io_version_id UUID NOT NULL REFERENCES io_versions(id),
  
  -- Granularity
  annotation_level TEXT NOT NULL
    CHECK (annotation_level IN ('word', 'sentence', 'paragraph', 'article')),
  -- For sub-article annotations: text range or element path
  target_selector JSONB, -- {"start_offset": 0, "end_offset": 50, "section_index": 2}
  
  -- Type
  annotation_type TEXT NOT NULL
    CHECK (annotation_type IN ('fact_check', 'correction', 'context', 'personal_experience',
                                'expert_insight', 'question', 'counterpoint',
                                'additional_source', 'flag_misleading')),
  
  -- Content
  author_id UUID NOT NULL REFERENCES users(id),
  body TEXT NOT NULL,
  evidence_urls TEXT[],
  
  -- Community feedback
  useful_votes INTEGER NOT NULL DEFAULT 0,
  not_useful_votes INTEGER NOT NULL DEFAULT 0,
  
  -- Moderation
  status TEXT NOT NULL DEFAULT 'active'
    CHECK (status IN ('active', 'hidden', 'removed', 'featured')),
  moderation_reason TEXT,
  
  -- For fact-checks specifically
  fact_check_verdict TEXT
    CHECK (fact_check_verdict IN ('confirmed', 'partially_true', 'misleading',
                                   'unverified', 'false', NULL))
);


-- ═══════════════════════════════════════════════════════════════
-- GOVERNMENT AGENCY CONTENT (B2G Layer)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE agency_publications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  agency_id UUID NOT NULL REFERENCES publishers(id),
  
  -- Original publication
  title_de TEXT,
  title_fr TEXT,
  title_it TEXT,
  original_url TEXT NOT NULL,
  publication_date DATE,
  publication_type TEXT
    CHECK (publication_type IN ('report', 'statistics', 'press_release',
                                 'regulation', 'guideline', 'dataset', 'alert')),
  
  -- Processing
  raw_content_path TEXT, -- S3 path to original PDF/document
  synthesized_io_id UUID REFERENCES intelligence_objects(id),
  synthesis_status TEXT DEFAULT 'pending'
    CHECK (synthesis_status IN ('pending', 'processing', 'review', 'published', 'failed')),
  
  -- Analytics (for B2G reporting)
  views_count INTEGER NOT NULL DEFAULT 0,
  unique_readers INTEGER NOT NULL DEFAULT 0,
  avg_reading_time_seconds FLOAT,
  shares_count INTEGER NOT NULL DEFAULT 0
);


-- ═══════════════════════════════════════════════════════════════
-- DEMOCRACY TOOLKIT
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE votes_and_initiatives (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Classification
  vote_type TEXT NOT NULL
    CHECK (vote_type IN ('federal_initiative', 'federal_referendum', 'cantonal_vote',
                          'communal_vote', 'parliamentary_vote')),
  level TEXT NOT NULL CHECK (level IN ('federal', 'cantonal', 'communal')),
  canton TEXT, -- NULL for federal
  commune_bfs_number INTEGER, -- NULL for federal/cantonal
  
  -- Details
  title_de TEXT,
  title_fr TEXT,
  title_it TEXT,
  official_url TEXT,
  vote_date DATE,
  
  -- Status
  status TEXT NOT NULL
    CHECK (status IN ('upcoming', 'active', 'completed')),
  result JSONB, -- {"yes_percent": 52.3, "no_percent": 47.7, "turnout": 45.2, "cantons_yes": 14}
  
  -- AI analysis
  synthesized_io_id UUID REFERENCES intelligence_objects(id),
  pro_arguments JSONB, -- AI-synthesized from all sources
  contra_arguments JSONB,
  financial_impact JSONB,
  historical_precedents UUID[], -- related past votes
  
  -- Curia Vista link
  curia_vista_id TEXT
);


-- ═══════════════════════════════════════════════════════════════
-- MIND MAP / RESEARCH WORKSPACE
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE mindmap_boards (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  title TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  is_shared BOOLEAN NOT NULL DEFAULT false,
  shared_with UUID[] -- user IDs
);

CREATE TABLE mindmap_nodes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  board_id UUID NOT NULL REFERENCES mindmap_boards(id) ON DELETE CASCADE,
  
  -- What this node contains
  node_type TEXT NOT NULL
    CHECK (node_type IN ('io_clip', 'entity_card', 'note', 'source_link',
                          'annotation', 'ai_suggestion', 'image', 'data_point')),
  
  -- Reference to source content
  io_id UUID REFERENCES intelligence_objects(id),
  entity_id UUID REFERENCES entities(id),
  
  -- Node content
  title TEXT,
  body TEXT,
  metadata JSONB DEFAULT '{}',
  
  -- Canvas position
  position_x FLOAT NOT NULL DEFAULT 0,
  position_y FLOAT NOT NULL DEFAULT 0,
  width FLOAT,
  height FLOAT,
  color TEXT
);

CREATE TABLE mindmap_edges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  board_id UUID NOT NULL REFERENCES mindmap_boards(id) ON DELETE CASCADE,
  source_node_id UUID NOT NULL REFERENCES mindmap_nodes(id) ON DELETE CASCADE,
  target_node_id UUID NOT NULL REFERENCES mindmap_nodes(id) ON DELETE CASCADE,
  label TEXT,
  edge_type TEXT DEFAULT 'manual'
    CHECK (edge_type IN ('manual', 'ai_suggested', 'entity_relation'))
);
```

---

## 7. INGESTION ENGINE (THE CRAWLER)

### Architecture

The ingestion engine is a distributed, priority-based crawler that respects legal constraints
at every step. It runs as a set of Celery workers with the following job types:

### Job Types & Priority

| Priority | Job Type | Interval | Sources |
|----------|----------|----------|---------|
| P0 (Real-time) | Government alerts | 1 min | AlertSwiss, MeteoSchweiz, SNB |
| P1 (Near real-time) | Wire services | 5 min | Keystone-SDA, AP (when licensed) |
| P2 (Frequent) | RSS monitoring | 15 min | All publisher RSS feeds |
| P3 (Regular) | Government publications | 1 hour | admin.ch, BFS, cantonal sites |
| P4 (Periodic) | Open data refresh | 6 hours | opendata.swiss, SOGC, courts |
| P5 (Daily) | Deep scrape | 24 hours | Social signals, forum monitoring |
| P6 (Weekly) | Entity enrichment | 7 days | Lobbywatch, Wikidata, SOGC updates |

### Government Data Sources (Phase 0 — Fully Legal)

```python
GOVERNMENT_SOURCES = {
    # ── Federal Level ──────────────────────────────────────────
    "admin_ch": {
        "url": "https://www.admin.ch/gov/de/start.html",
        "type": "government",
        "rss": "https://www.admin.ch/gov/de/start.html.rss",
        "languages": ["de", "fr", "it"],
        "content": "Federal Council press releases, decisions, reports",
        "license": "public_domain",
        "can_synthesize": True,
        "scrape_interval_minutes": 30,
    },
    "curia_vista": {
        "api": "https://ws.parlament.ch/odata.svc/",
        "alt_api": "https://openparldata.ch/api/v1/",
        "type": "government",
        "content": "Parliamentary affairs, votes, councillor data, sessions",
        "license": "public_domain",
        "can_synthesize": True,
        "note": "OData API with 43 tables. Also available via OpenParlData REST API "
                "covering 78 national/cantonal/municipal parliaments.",
    },
    "opendata_swiss": {
        "api": "https://ckan.opendata.swiss/api/3/action/",
        "type": "open_data",
        "content": "14,279 datasets from 65+ organizations",
        "license": "open_license",
        "can_synthesize": True,
        "note": "CKAN-based. Use package_search, package_show, organization_list. "
                "Apache Lucene search syntax. Each dataset has downloadUrl or accessUrl.",
    },
    "bfs": {
        "api": "https://data.bfs.admin.ch/",
        "alt_api": "BFS Swiss Stats Explorer (SSE) API",
        "type": "government",
        "content": "Population, economy, education, health, environment statistics",
        "license": "public_domain",
        "can_synthesize": True,
        "note": "Machine-readable datasets in CSV, JSON, XLSX. API supports "
                "language parameter (de/fr/it/en). ~184 English datasets, thousands in DE/FR.",
    },
    "bfu": {
        "url": "https://www.bfu.ch/",
        "type": "government",
        "content": "Accident prevention reports, safety statistics, campaigns",
        "license": "public_domain",
        "can_synthesize": True,
    },
    "sogc_shab": {
        "url": "https://www.shab.ch/",
        "api": "REST API available via Amtsblattportal",
        "type": "government",
        "content": "Company registrations, bankruptcies, changes, official announcements",
        "license": "public_domain",
        "can_synthesize": True,
        "note": "Gold mine for business news. Every new company, every bankruptcy, "
                "every board change is published here before anywhere else.",
    },
    "entscheidsuche": {
        "url": "https://entscheidsuche.ch/",
        "type": "government",
        "content": "Court decisions from all Swiss courts at all levels",
        "license": "public_domain",
        "can_synthesize": True,
    },
    "fedlex": {
        "url": "https://www.fedlex.admin.ch/",
        "type": "government",
        "content": "Federal law, SR numbers, legislative changes",
        "license": "public_domain",
        "can_synthesize": True,
    },
    "snb": {
        "url": "https://data.snb.ch/",
        "type": "government",
        "content": "Monetary policy, interest rates, exchange rates, financial stability",
        "license": "public_domain",
        "can_synthesize": True,
    },
    "meteoswiss": {
        "api": "https://opendata.swiss (MeteoSwiss datasets)",
        "type": "government",
        "content": "Weather data, climate projections, natural hazard alerts",
        "license": "open_license",
        "can_synthesize": True,
    },
    "sbb_transport": {
        "api": "https://opentransportdata.swiss/",
        "type": "government",
        "content": "Public transport data, disruptions, timetables",
        "license": "open_license",
        "can_synthesize": True,
    },
    
    # ── Additional Federal Agencies ────────────────────────────
    "bag_health": {"url": "https://www.bag.admin.ch/", "content": "Public health"},
    "bafu_environment": {"url": "https://www.bafu.admin.ch/", "content": "Environment"},
    "seco_economy": {"url": "https://www.seco.admin.ch/", "content": "Economic affairs"},
    "bfe_energy": {"url": "https://www.bfe.admin.ch/", "content": "Energy"},
    "astra_roads": {"url": "https://www.astra.admin.ch/", "content": "Roads, traffic"},
    "sem_migration": {"url": "https://www.sem.admin.ch/", "content": "Migration, asylum"},
    "fedpol": {"url": "https://www.fedpol.admin.ch/", "content": "Police, security"},
    "ige_ip": {"url": "https://www.ige.ch/", "content": "Patents, trademarks"},
    "sbfi_education": {"url": "https://www.sbfi.admin.ch/", "content": "Education, research"},
    "swissmedic": {"url": "https://www.swissmedic.ch/", "content": "Drug approvals, alerts"},
    "alertswiss": {"url": "https://www.alert.swiss/", "content": "Emergency alerts"},
    
    # ── Cantonal Open Data Portals ─────────────────────────────
    "zh_opendata": {"api": "https://data.stadt-zuerich.ch/", "canton": "ZH"},
    "be_opendata": {"api": "https://www.bern.ch/open-government-data-ogd", "canton": "BE"},
    "bs_opendata": {"api": "https://data.bs.ch/", "canton": "BS"},
    "ge_opendata": {"api": "https://ge.ch/sitg/", "canton": "GE"},
    "vd_opendata": {"api": "https://www.vd.ch/themes/etat-droit-finances/statistique/", "canton": "VD"},
    
    # ── Additional Public Data ─────────────────────────────────
    "lobbywatch": {"api": "https://lobbywatch.ch/", "content": "Political transparency data"},
    "srgssr_api": {"api": "SRG SSR public APIs", "content": "Public broadcaster content"},
    "openerz": {"api": "OpenERZ API", "content": "Waste collection data (multi-commune)"},
    "openplz": {"api": "OpenPLZ API", "content": "Street and postal code directory CH/DE/AT/LI"},
}
```

### RSS Feed Registry (Phase 0-1)

```python
# These RSS feeds are PUBLISHED by the source for machine consumption.
# Reading them is explicitly intended and legal.
RSS_FEEDS = {
    # ── National Media ─────────────────────────────────────────
    "nzz": [
        {"url": "https://www.nzz.ch/recent.rss", "lang": "de", "category": "general"},
    ],
    "tagesanzeiger": [
        {"url": "https://www.tagesanzeiger.ch/rss", "lang": "de", "category": "general"},
    ],
    "srf": [
        {"url": "https://www.srf.ch/news/bnf/rss/1890", "lang": "de", "category": "news"},
    ],
    "rts": [
        {"url": "https://www.rts.ch/info/rss", "lang": "fr", "category": "news"},
    ],
    "watson": [
        {"url": "https://www.watson.ch/api/1.0/rss/index.xml", "lang": "de"},
    ],
    "20min_de": [
        {"url": "https://www.20min.ch/rss/", "lang": "de"},
    ],
    "20min_fr": [
        {"url": "https://www.20minutes.ch/rss/", "lang": "fr"},
    ],
    "blick": [
        {"url": "https://www.blick.ch/rss", "lang": "de"},
    ],
    "letemps": [
        {"url": "https://www.letemps.ch/rss", "lang": "fr"},
    ],
    "republik": [
        {"url": "https://www.republik.ch/feed", "lang": "de"},
    ],
    "swissinfo": [
        {"url": "https://www.swissinfo.ch/eng/rss", "lang": "en"},
        {"url": "https://www.swissinfo.ch/ger/rss", "lang": "de"},
        {"url": "https://www.swissinfo.ch/fre/rss", "lang": "fr"},
    ],
    # ── Regional Media ─────────────────────────────────────────
    "bernerzeitung": [{"url": "...", "lang": "de", "canton": "BE"}],
    "basellandschaftliche": [{"url": "...", "lang": "de", "canton": "BL"}],
    "luzernerzeitung": [{"url": "...", "lang": "de", "canton": "LU"}],
    "suedostschweiz": [{"url": "...", "lang": "de", "cantons": ["GR", "GL", "SZ"]}],
    # ... extend for all regional outlets
    
    # ── International (Switzerland coverage) ───────────────────
    "reuters_ch": [{"url": "...", "lang": "en", "filter": "switzerland"}],
    "bloomberg_ch": [{"url": "...", "lang": "en", "filter": "switzerland"}],
}
```

### Ingestion Pipeline Flow

```
1. FETCH: Download RSS/API/webpage
   ↓
2. DEDUP: Check if URL already exists in sources table
   ↓
3. CLASSIFY: Local Llama classifies source_type + category + language
   ↓
4. LEGAL CHECK: Verify license_status against publisher config
   ├─ public_domain/open_license/licensed → proceed to full processing
   ├─ rss_metadata_only → extract headline + snippet + URL only
   └─ unlicensed → extract factual metadata only (entities, topic, date)
   ↓
5. EXTRACT: NER (entities), topic classification, sentiment, key facts
   ↓
6. EMBED: Generate multilingual embedding (Cohere/BGE-M3)
   ↓
7. CLUSTER: Find existing IO that matches this event (cosine similarity > 0.85)
   ├─ Match found → add source to existing IO, trigger re-synthesis
   └─ No match → create new IO candidate, queue for editorial triage
   ↓
8. STORE: Insert source record with all metadata and legal flags
```

---

## 8. SYNTHESIS ENGINE (THE BRAIN)

### Core Process

When an IO needs synthesis (new IO or existing IO with new source):

```
1. GATHER: Collect all sources assigned to this IO
   ↓
2. FILTER: Only sources where can_synthesize_from = true
   ↓
3. EXTRACT FACTS: From each qualifying source, extract:
   - Verified claims (who, what, when, where)
   - Attributed opinions/interpretations (who said what)
   - Contested points (source A says X, source B says Y)
   - Missing information (what questions remain unanswered)
   ↓
4. SYNTHESIZE: Claude API call with structured prompt:
   
   System: "You are a Swiss news synthesis engine. Your output must be:
   - ORIGINAL expression (never paraphrase or closely mirror any source)
   - Structured as: Factual Core → Interpretation Layer → Context Layer → Missing Voices
   - Neutral in tone — present all perspectives with attribution
   - Include source citations as [Source: publisher_name] inline
   - Flag contradictions explicitly
   - Note missing stakeholder voices
   - Separate confirmed facts from unverified claims
   Generate in {language}. Write for an educated Swiss audience."
   
   User: "Synthesize the following event from {n} sources:
   
   CONFIRMED FACTS:
   {extracted_facts}
   
   ATTRIBUTED STATEMENTS:
   {attributed_quotes}
   
   CONTRADICTIONS:
   {contradictions}
   
   CONTEXT FROM KNOWLEDGE GRAPH:
   {entity_context, historical_precedents, related_government_data}
   
   Output as JSON:
   {
     'title': '',
     'lead': '', (max 2 sentences)
     'sections': [
       {'type': 'factual_core', 'content': '...'},
       {'type': 'interpretation', 'content': '...', 'attributions': [...]},
       {'type': 'context', 'content': '...'},
       {'type': 'missing_voices', 'content': '...'}
     ],
     'summary': '', (max 100 words)
     'quality_assessment': {
       'confirmation_density': 0.0-1.0,
       'completeness_score': 0.0-1.0,
       'missing_elements': ['...']
     }
   }"
   ↓
5. REVIEW: Queue for editorial review (if not auto-approved)
   ↓
6. VERSION: Create new io_version record, update IO metadata
   ↓
7. NOTIFY: Alert users who read/shared a previous version
   ↓
8. EMBED: Generate new embedding for the IO, update vector index
```

### Synthesis Quality Rules

- NEVER reproduce more than 10 consecutive words from any single source
- ALWAYS attribute interpretive claims to their source
- ALWAYS note when only one source reports a claim
- ALWAYS include the "Missing Voices" section if any stakeholder hasn't been heard from
- NEVER present speculation as fact
- ALWAYS distinguish between "confirmed by multiple independent sources" and "reported by one source"
- For each version, generate a structured diff from the previous version

### Language Strategy

Each language version is synthesized INDEPENDENTLY from sources in that language, then
ENRICHED with facts only available in other languages:

```
DE version: Primarily from DE sources + facts from FR/IT/EN sources not available in DE
FR version: Primarily from FR sources + facts from DE/IT/EN sources not available in FR
IT version: Primarily from IT sources + facts from DE/FR/EN sources not available in IT
EN version: Synthesized from all sources (serves as the most complete version)
```

---

## 9. KNOWLEDGE GRAPH (THE MEMORY)

### Entity Resolution

When NER extracts an entity name, the resolution pipeline:

1. Exact match against canonical_name and all aliases
2. Fuzzy match (Levenshtein distance < 3) against all names
3. Cross-language match (e.g., "Berne" = "Bern" = "Berna")
4. Context-aware disambiguation (e.g., "UBS" the bank vs "UBS" the abbreviation in another context)
5. If no match: create candidate entity, queue for enrichment

### Auto-Enrichment Sources

- Wikidata: structured data for all notable entities
- Lobbywatch.ch: political transparency data (mandates, interests, connections)
- SOGC/SHAB: company data (UID, board members, capital changes)
- Handelsregister: cantonal commercial registers
- BFS commune register: geographic entities
- Curia Vista: parliamentarian data, voting records

### Self-Healing Mechanisms

Run as scheduled jobs:

1. **Entity Deduplication** (daily): Find entity pairs with high embedding similarity,
   merge if confirmed by cross-referencing external IDs
2. **Stale Link Detection** (6 hours): Check source URLs for 404/moved, update or flag
3. **Contradiction Resolution** (on new source): When new information contradicts existing
   IO synthesis, flag for re-synthesis and user notification
4. **Embedding Drift Correction** (weekly): Re-embed entities and IOs when embedding model
   is updated, with version tracking
5. **Source Health Monitoring** (hourly): Detect when a publisher's RSS/API goes offline,
   changes URL structure, or alters content policy
6. **Orphaned Entity Cleanup** (weekly): Remove entities with zero mentions that haven't
   been referenced in 90 days

---

## 10. API LAYER

### Public API (for Pro/Enterprise tiers)

```
Base URL: https://api.signal.ch/v1/

Authentication: Bearer token (API key)
Rate limits: Pro = 1000 req/day, Enterprise = 10000 req/day

GET  /ios                    # List IOs (filterable by category, scope, canton, date)
GET  /ios/:id                # Get IO with current synthesis
GET  /ios/:id/versions       # Get version history
GET  /ios/:id/sources        # Get source list with provenance
GET  /ios/:id/entities       # Get related entities

GET  /entities               # Search entities
GET  /entities/:id           # Get entity profile
GET  /entities/:id/ios       # Get all IOs mentioning this entity
GET  /entities/:id/relations # Get knowledge graph connections

GET  /search                 # Full-text search
POST /search/conversational  # Natural language query (Claude-powered)

GET  /votes                  # Upcoming and recent votes
GET  /votes/:id              # Vote details with AI analysis

GET  /briefs/daily           # Personalized daily brief (requires auth)
GET  /briefs/breaking        # Breaking news stream (WebSocket upgrade available)

# Webhooks (Enterprise)
POST /webhooks               # Register webhook for topics/entities/cantons
```

### Internal API (between services)

- Ingestion → Synthesis: via Redis Streams (job queue)
- Synthesis → Knowledge Graph: direct DB writes + event emission
- All services → Monitoring: structured logging to Loki

---

## 11. FRONTEND APPLICATION

### Design Language

- **Aesthetic**: Editorial precision meets Swiss modernism. Think NZZ's typography + Bloomberg's
  data density + Republik's reading experience. NOT generic SaaS.
- **Color palette**: Deep navy (#0F172A) primary, Swiss red (#DC2626) for breaking/alerts,
  warm gray (#F8FAFC) backgrounds, blue (#2563EB) for interactive elements
- **Typography**: Serif for article text (Georgia, Lora, or Source Serif Pro), sans-serif for
  UI (Inter or custom Swiss Grotesk), monospace for data
- **Dark mode**: First-class citizen, not an afterthought
- **Density**: Information-dense by default, with progressive disclosure
- **Motion**: Minimal, purposeful. Version transitions, trust indicator animations.

### Core Pages

1. **Home / Feed**: Personalized stream of IOs ranked by relevance, recency, importance.
   Blind spot injections interspersed. Filterable by category, scope, canton, language.

2. **IO Detail**: The flagship page. Shows:
   - Current synthesis with quality constellation indicators
   - Source genome sidebar (all contributing sources with reliability indicators)
   - Entity cards (inline, expandable)
   - Version timeline (scrubber showing evolution)
   - Annotation layer (toggle on/off, shows community annotations at all granularity levels)
   - Bias spectrum visualization
   - Related IOs
   - "What's missing" section

3. **Entity Profile**: Deep profile for any person/org/company:
   - Timeline of all mentions across IOs
   - Relationship graph (visual network)
   - Sentiment trend over time
   - For politicians: voting record, Lobbywatch data, financial interests
   - For companies: SOGC filings, litigation, market data

4. **Search**: Dual mode:
   - Instant text search (Meilisearch)
   - Conversational AI search (Claude-powered, full knowledge graph access)

5. **Daily Brief**: Morning/evening briefing, configurable:
   - Time-aware (adapts to available reading time)
   - Audio toggle (TTS version)
   - Blind spot section
   - Voting reminders

6. **Mind Map Workspace** (Pro+): Infinite canvas for research:
   - Drag-and-drop IO clips, entity cards, annotations, notes
   - AI-suggested connections between nodes
   - Export as report, presentation, or structured data
   - Shareable (Enterprise)

7. **Democracy Toolkit**: Votes and initiatives hub:
   - Upcoming votes with AI-synthesized pro/contra
   - Vote calendar
   - Gemeinde monitor
   - Parliamentary watch (follow specific topics or parliamentarians)

8. **Settings / Profile**: Language, notifications, privacy controls, subscription management,
   data export (GDPR/nDSG), account deletion

### Mobile Considerations

- Offline-capable (Service Worker for cached briefs)
- Audio-first mode for commuting
- Swipe gestures for IO navigation
- Push notifications for breaking news
- Widget for home screen (today's brief summary)

---

## 12. AI PODCAST & MEDIA GENERATION

### Podcast Formats

| Format | Duration | Frequency | Description |
|--------|----------|-----------|-------------|
| Morning Signal | 10 min | Daily | Two AI hosts discuss top 5 stories, conversational |
| Deep Signal | 30 min | Weekly | Single topic deep-dive with synthesized expert views |
| Stammtisch | 15 min | Daily | Two AI personas argue different political perspectives |
| Mein Kanton | 5 min | Daily | Hyper-local briefing per canton (26 versions) |

### Generation Pipeline

```
1. SELECT: Curate stories for today's episode (editorial + algorithmic)
2. SCRIPT: Claude generates conversational script in target language
   - Two distinct "host" personas with different speaking styles
   - Natural conversation dynamics: agreement, pushback, humor, clarification
   - Include source citations verbally ("According to the NZZ...")
3. VOICE: TTS generation (Eleven Labs or XTTS v2)
   - Distinct voices per host
   - Swiss German cadence option (for informal formats)
4. MIX: Add intro/outro music, transitions, sound design
5. PUBLISH: Distribute via RSS (podcast standard), in-app, and embed on Signal.ch
```

### Video Briefs

- 60-second AI-generated news summaries
- Stylized AI anchor (clearly AI, distinctive Swiss design, not uncanny valley)
- Dynamic graphics, maps, data visualizations
- Licensed or public domain footage only (or AI-generated illustrations)
- Daily and breaking formats

---

## 13. USER SYSTEM & PERSONALIZATION

### Personalization Algorithm

```
user_feed = weighted_merge(
    relevance_to_interests(user.interests, io.category, io.entities),  # 40%
    geographic_proximity(user.canton, user.commune, io.scope, io.cantons),  # 25%
    recency(io.last_source_added_at),  # 15%
    importance(io.confirmation_density, io.source_count),  # 10%
    blind_spot_injection(user.reading_history, io.category),  # 10%
)
```

### Blind Spot Algorithm

Analyze user's reading history over the last 30 days. Identify:
- Categories they never read
- Cantons/regions they never see
- Languages they don't consume
- Political perspectives they're underexposed to

Inject 1-2 blind spot stories per brief. User rates these (helpful/not relevant), which
trains the blind spot sensitivity parameter.

### Version Notification

When a user has read or shared an IO, and that IO is subsequently updated with material
changes:

```
IF (diff_significance(old_version, new_version) > threshold):
  notify_user({
    type: "io_updated",
    message: "The article you {read/shared} about {topic} has been substantially updated.",
    changes_summary: diff_summary,
    user_version: version_number_they_read,
    current_version: current_version_number,
    diff_link: "/io/{id}/diff/{old_version}/{new_version}"
  })
```

---

## 14. COMMENT & ANNOTATION SYSTEM

### Structured Response Types

When a user comments, they choose a type:

| Type | Template | Weight |
|------|----------|--------|
| Personal Experience | "I witnessed..." / "In my experience..." | Location-weighted |
| Expert Insight | Requires verified expertise badge | High weight |
| Correction | Must include evidence URL | Queued for editorial review |
| Question | "What about..." / "Has anyone..." | Surfaced for editorial follow-up |
| Counterpoint | "However..." / "An alternative view..." | Shown in opposing perspectives |
| Additional Source | Must include URL | Auto-checked for relevance |

### Reputation System

- Upvotes based on "was this useful?" (NOT "do I agree?")
- Verified expertise badges (self-declared, community-validated, or credential-verified)
- Annotation accuracy score (how often fact-checks are confirmed)
- Troll/spam quietly deprioritized (never publicly labeled)

---

## 15. DEMOCRACY TOOLKIT

### Data Sources

- Bundeskanzlei: upcoming Abstimmungen with official texts
- Curia Vista: parliamentary initiatives, motions, interpellations
- OpenParlData.ch: harmonized data from 78 parliaments (national + cantonal + municipal)
- Cantonal chancelleries: cantonal votes
- Communal websites: Gemeindeversammlungen agendas

### Features

- **Abstimmungs-Radar**: Every upcoming vote with AI-synthesized pro/contra from all sources
- **Petition Tracker**: Active federal and cantonal petitions, signature progress
- **Parliamentary Watch**: Follow specific parliamentarians or topics across all government levels
- **Gemeinde Monitor**: Your commune's decisions, budget, building plans, upcoming meetings
- **Voting Reminder**: Push notification 12 days before vote with Signal.ch analysis

---

## 16. SEARCH & CONVERSATIONAL AI

### Instant Search (Meilisearch)

- Full-text indexing of all IO titles, leads, summaries (not full synthesis — too much)
- Entity name search
- Faceted search: category, scope, canton, date range, language, source type
- Swiss-specific: handles German compounds, French accents, Italian particularities
- Response time target: <50ms

### Conversational Search (Claude-powered, Pro+)

User types natural language query. System:

1. Classifies intent (factual lookup, relationship query, trend analysis, comparison)
2. Generates structured query against knowledge graph
3. Retrieves relevant IOs, entities, and data points
4. Claude synthesizes a cited, explorable response
5. Response includes interactive elements: entity cards, IO links, data visualizations

Examples:
- "What's the connection between UBS restructuring and new FINMA regulations?"
- "Show me all building permits denied in Bern in the last 6 months"
- "How has Zurich's rental market changed since the last interest rate decision?"
- "Compare how NZZ and Blick covered the latest Federal Council decision"

---

## 17. NOTIFICATION INTELLIGENCE

### Priority Levels

| Level | Trigger | Delivery |
|-------|---------|----------|
| Breaking | Genuine breaking news (earthquake, major political event) | Immediate push |
| Urgent | Significant update to followed topic/entity | Within 15 min |
| Digest | Morning/evening brief ready | Scheduled per user prefs |
| Update | IO the user read/shared has material update | Batched hourly |
| Proximity | Event within 5km of user location (opt-in) | Immediate if enabled |
| Democracy | Upcoming vote, petition deadline | 12 days, 3 days, 1 day before |

### Activity-Aware Delivery

If user grants calendar/health API access (explicit opt-in):
- Commuting: Audio brief format
- At work: Text digest, minimal interruption
- Exercising: Podcast format
- Relaxing: Deep reads suggested

---

## 18. ADVERTISING ENGINE

### Principles

1. NEVER inline or disguised as content (Art. 3 lit. o UWG compliance)
2. Contextual matching only (topic of article, not user tracking)
3. User-controlled: "Why am I seeing this?", category opt-outs, frequency caps
4. Quality-gated: No crypto scams, miracle cures, political manipulation
5. Swiss advertisers prioritized
6. Revenue share on citizen journalism content

### Implementation

- Separate ad container component, visually distinct (different background, "Anzeige" label)
- Contextual targeting: match ad categories to IO categories and entities
- No cross-site tracking pixels
- No third-party ad networks initially — direct sales + programmatic via Swiss ad exchanges
- CMP integration for FADP/Google consent requirements

---

## 19. GOVERNMENT AGENCY B2G PORTAL

### Features

- Agency dashboard: upload publications, track synthesis status
- Analytics: views, unique readers, reading time, shares, geographic distribution
- Monthly reach reports (PDF export for agency communications departments)
- Multi-language synthesis status tracking
- API for automated publication submission

### Pricing

- CHF 2,000/month: Basic (up to 5 publications/month, standard analytics)
- CHF 3,500/month: Professional (unlimited publications, advanced analytics, API access)
- CHF 5,000/month: Enterprise (dedicated synthesis priority, custom branding, presentation-ready reports)

---

## 20. ADMIN & EDITORIAL DASHBOARD

### Editorial Queue

- All AI-generated synthesis queued for review before publication
- Side-by-side view: synthesis vs. contributing sources
- One-click approve, reject, or edit
- Bulk operations for routine content (government press releases)
- Quality metrics: how often editors change AI synthesis, common error patterns

### Admin Functions

- Publisher management (add/remove, license tracking, reliability score override)
- User management (tier management, bans, verified expertise badges)
- Content moderation (flagged annotations, reported IOs)
- System health dashboard (scraper status, synthesis queue depth, API latency)
- License compliance audit (verify all published content has valid license chain)
- Financial dashboard (subscription revenue, ad revenue, agency contracts)

---

## 21. MONITORING, HEALTH & SELF-HEALING

### Metrics to Track

- Ingestion: sources scraped/hour, success rate, new sources/day, dedup rate
- Synthesis: queue depth, avg synthesis time, editorial rejection rate
- Knowledge graph: entity count, relation count, dedup merges/day
- API: request count, latency p50/p95/p99, error rate
- Frontend: page load time, Core Web Vitals, user engagement metrics
- Business: DAU/WAU/MAU, paid conversion rate, churn rate, ARPU

### Alerts

- Ingestion failure rate > 10% → alert engineering
- Synthesis queue > 100 items → scale workers
- Editorial rejection rate > 30% → review synthesis prompts
- Publisher RSS offline > 6 hours → alert + fallback strategy
- Database disk > 80% → alert + auto-scaling trigger
- Any nDSG-relevant data breach → immediate incident response

---

## 22. DEPLOYMENT & DEVOPS

### Environments

- `dev`: Local Docker Compose, SQLite for fast iteration
- `staging`: Infomaniak, mirrors production, anonymized data
- `production`: Infomaniak primary, Hetzner ML, Cloudflare CDN

### CI/CD Pipeline

```
push to main → GitHub Actions:
  1. Lint (ruff, eslint)
  2. Type check (mypy, TypeScript)
  3. Unit tests (pytest, vitest)
  4. Integration tests (against staging DB)
  5. Build containers
  6. Deploy to staging (auto)
  7. Deploy to production (manual approval)
```

### Backup Strategy

- PostgreSQL: pg_dump daily, WAL archiving for point-in-time recovery
- Object storage: cross-region replication
- Configuration: Git-managed, encrypted secrets via SOPS or Vault

---

## 23. PHASE ROADMAP & BUILD ORDER

### Phase 0: Government Intelligence Layer (Weeks 1-12)

**Build order (strict):**

1. Database schema (PostgreSQL + pgvector setup)
2. Publisher registry (seed with all government sources)
3. Ingestion engine: admin.ch RSS scraper
4. Ingestion engine: opendata.swiss CKAN API connector
5. Ingestion engine: Curia Vista / OpenParlData connector
6. Ingestion engine: SOGC/SHAB connector
7. Ingestion engine: BFS API connector
8. NER pipeline (entity extraction from government text)
9. Entity resolution & knowledge graph population
10. Embedding pipeline (all sources + entities)
11. Synthesis engine: first IO generation from government sources
12. Editorial review queue (basic approve/reject)
13. Frontend: IO list view + IO detail page
14. Frontend: Entity profile page
15. Frontend: Basic search (Meilisearch)
16. Frontend: Daily brief (government-only)
17. API: Basic read endpoints
18. Auth: User registration + login
19. Admin dashboard: basic editorial tools

**Deliverable**: Working product showing Swiss government intelligence, searchable, with
entity profiles and knowledge graph. Zero licensing cost. Fully legal.

### Phase 1: Nau.ch Partnership + News Layer (Weeks 13-24)

20. RSS feed monitoring for all major Swiss outlets
21. Event detection & IO clustering from RSS metadata
22. Integration with nau.ch content feed (per partnership agreement)
23. Expanded synthesis (nau.ch content + government data overlay)
24. Annotation system (basic: article-level comments)
25. Frontend: Bias spectrum visualization
26. Frontend: Source genome sidebar
27. Frontend: Version timeline with diff view
28. User personalization: interests, canton, language
29. Blind spot algorithm
30. Push notifications (basic)
31. TTS: Daily brief audio version
32. B2G portal: basic agency dashboard

### Phase 2: Premium Features + Revenue (Weeks 25-48)

33. Freemium gating (tier enforcement)
34. Stripe integration (subscription management)
35. Conversational search (Claude-powered)
36. Mind map workspace
37. Democracy toolkit (Abstimmungs-Radar, parliamentary watch)
38. AI podcast generation (Morning Signal format)
39. Expanded annotation system (sentence-level, word-level)
40. Reputation system
41. Contextual advertising engine
42. Enterprise tier: team workspaces, API access, webhooks
43. Mobile app (or responsive PWA)
44. Citizen journalism submission system

### Phase 3: Full Platform (Weeks 49-72)

45. Video brief generation
46. Full podcast suite (Stammtisch, Deep Signal, Mein Kanton)
47. Advanced entity enrichment (Lobbywatch integration, conflict of interest detector)
48. API marketplace
49. Sentiment analysis of external comment sections
50. Smart notifications (activity-aware)
51. White-label solutions for cantons/communes
52. Romansh language support (stretch)

---

## 24. CODING CONVENTIONS & INVARIANTS

### Python Backend

- Python 3.12+, strict type hints everywhere
- FastAPI with Pydantic v2 models for all request/response schemas
- async/await for all I/O-bound operations
- ruff for linting + formatting (replaces black + isort + flake8)
- pytest for testing, minimum 80% coverage on business logic
- Alembic for database migrations
- Environment variables for all secrets (never in code)
- Structured logging (JSON format) via structlog

### Frontend

- TypeScript strict mode
- Next.js 14+ App Router
- Server components by default, client components only when needed
- Tailwind CSS, no CSS-in-JS
- Zustand for client state
- React Query / SWR for server state
- Accessibility: WCAG 2.1 AA minimum
- i18n: next-intl, all strings externalized, DE/FR/IT/EN from day one

### Database

- UUIDs for all primary keys (never auto-increment integers)
- TIMESTAMPTZ for all timestamps (never TIMESTAMP)
- JSONB for structured flexible data (with documented schemas in comments)
- Indexes on every foreign key and every column used in WHERE clauses
- Row-Level Security (RLS) for multi-tenancy if using Supabase
- All migrations reversible

### Security

- HTTPS everywhere (Caddy auto-TLS)
- API keys: hashed storage, scoped permissions, rotation support
- User passwords: Argon2id (via Supabase Auth or similar)
- Encryption at rest for sensitive content (full_text_encrypted columns)
- CORS: strict origin whitelist
- Rate limiting: per-user, per-IP, per-endpoint
- CSP headers, no inline scripts
- Regular dependency audits (dependabot / safety)

### Invariants (NEVER Violate)

1. Every published IO MUST have at least one source with can_synthesize_from = true
2. Every source MUST have a valid license_status before entering synthesis pipeline
3. Every IO MUST have human editorial approval before first publication (Phase 0-2)
4. Every user-facing string MUST exist in all 4 languages (DE/FR/IT/EN)
5. Every API response MUST include attribution_text for any sourced content
6. Every user data operation MUST check consent flags before processing
7. No personal data may leave Swiss jurisdiction without explicit DPA
8. The system MUST be able to retract any IO and notify all affected users within 1 hour
9. Every entity merge MUST be reversible for 30 days
10. Every synthesis MUST be reproducible (same inputs → same structure, even if wording varies)

---

## 25. CHALLENGE CATALOGUE — QUESTIONS THAT TESTED THIS PLAN

Before writing this prompt, the following hard questions were posed and resolved:

### Q1: "If we synthesize from scraped articles, aren't we just laundering copyright?"
RESOLUTION: The architecture separates FACT EXTRACTION (legal — facts aren't copyrightable)
from EXPRESSION GENERATION (our AI writes original text). The legal check at step 4 of the
ingestion pipeline (§7) gates all content. Sources without can_synthesize_from=true are
limited to metadata extraction only. Synthesis rules (§8): never reproduce >10 consecutive
words from any source, always attribute interpretive claims. Art. 25 CopA (quotation right)
covers short attributed excerpts within our original analytical work.

### Q2: "What happens when the Leistungsschutzrecht passes and we owe money retroactively?"
RESOLUTION: Phase 2 proactively approaches ProLitteris for voluntary collective licensing
BEFORE the law requires it. Creates goodwill and PR. Budget is allocated. The law targets
platforms reaching 10%+ of Swiss population — we won't hit that until Phase 3-4, buying
12-18 months of runway. The rejected bill (Oct 2025, 18-3) means the next version is still
12-18 months away from becoming law.

### Q3: "Government data is boring. How do you get 100K people to pay for it?"
RESOLUTION: Government data is the FOUNDATION, not the product. Users never see "government
data" — they see "The FINMA regulation you're reading about connects to these 3 Federal
Council decisions, this BFS report on financial stability, and this SOGC filing showing UBS
board changes." Government data is the CONTEXT that makes news synthesis 10x more valuable.

### Q4: "What if nau.ch says no?"
RESOLUTION: Phase 0 still works (government layer). Phase 1 pivots to smaller publishers
(Republik, Bajour, Hauptstadt). Phase 2 self-funds Keystone-SDA license from B2G revenue +
early subscribers. Timeline extends ~6 months but product remains viable.

### Q5: "How do you prevent AI hallucination in synthesized news?"
RESOLUTION: Multiple layers: (1) Synthesis from EXTRACTED VERIFIED FACTS only, never free
generation. (2) Completeness scoring flags gaps rather than filling them. (3) Every claim
traced to specific source(s). (4) Human editorial review mandatory in Phase 0-2.
(5) Community annotation for corrections. (6) Retraction within 1 hour (Invariant #8).

### Q6: "Swiss German dialect content will break NER."
RESOLUTION: Most published news is Standard German. For Mundart content: dialect-to-
Hochdeutsch preprocessing step (SwissGerman BERT exists). Entity extraction on normalized
text. Long-term: fine-tune NER on Swiss corpus.

### Q7: "4M nau.ch users are free/Pendler. How to convert to CHF 49-99?"
RESOLUTION: Nau.ch is funnel TOP. Conversion: Free → Personal (CHF 19) → Pro (CHF 49) →
Enterprise (CHF 99/seat). Blended ARPU target: CHF 30. B2G revenue is the early bridge.

### Q8: "The demo scrapes copyrighted content. What if nau.ch leaks it?"
RESOLUTION: Demo is internal R&D (Art. 19 CopA private use). NDA-protected meeting.
Demo labels scraped content as "demonstration only." Layer 1 presented as "production-ready
today." Layer 2 as "becomes legal when you bring your licenses."

### Q9: "What stops TX Group from building this with their Keystone-SDA ownership?"
RESOLUTION: They could but won't: (1) cannibalizes Tages-Anzeiger, 20 Minuten,
(2) neutral synthesis undermines editorial identity, (3) large media can't move this fast
on AI-native products. Our moat: knowledge graph + government data + entity resolution +
citizen community — all compound daily. If they build it anyway, validates category → acquisition.

### Q10: "CHF 900K-1.1M Year 1 — who funds this?"
RESOLUTION: (1) Nau.ch CHF 500K-1M. (2) B2G revenue Month 3-6. (3) Nord subsidizes Phase 0
dev costs. (4) Freemium revenue Month 6-9. (5) Peak burn ~CHF 920K at Month 16-17.
(6) Break-even Month 20-21. Clear path to profitability within 2 years.

### Q11: "SRG SSR has a public mandate and massive resources."
RESOLUTION: SRG SSR is a PARTNER. Constitutional mandate to serve all language regions.
Public APIs available. Publicly funded content. Long-term: they become a B2G customer.
Structurally constrained from building a commercial competitor.

### Q12: "Breaking news when synthesis takes 15 minutes?"
RESOLUTION: P0 real-time pipeline bypasses full synthesis. AlertSwiss, wire flashes,
government alerts published immediately as "developing" IOs (headline + confirmed facts +
source links). Full synthesis follows. IO status: flash → developing → synthesized →
reviewed → complete. Users see status clearly.

### Q13: "What about personality rights? AI synthesis of someone's statements?"
RESOLUTION: Art. 28 ZGB (personality rights) applies. The synthesis engine MUST attribute
all statements to their speakers. Never paraphrase in a way that alters meaning. The
editorial review queue catches misattribution. The annotation system allows subjects to
flag inaccurate representation. Retraction system handles errors quickly.

### Q14: "How do you handle a source that's later found to be fabricated?"
RESOLUTION: Source reliability tracking (§6, publishers table). If a source is flagged as
fabricated: (1) all IOs using that source are re-queued for synthesis WITHOUT it, (2) users
who read/shared affected IOs are notified, (3) the publisher's reliability_score is degraded,
(4) a transparency note is attached to affected IOs explaining the correction.

### Q15: "The four-language requirement quadruples development cost."
RESOLUTION: i18n is built in from line 1 (next-intl, externalized strings). The synthesis
engine generates multilingual content as part of its core function — it's not a separate
step. UI strings are a one-time translation cost (~2000 strings × 4 languages). The real
cost is editorial quality in FR/IT — addressed by hiring native speakers in Phase 2.

---

## 26. OPEN QUESTIONS & KNOWN RISKS

(Renumbered from §25 after insertion of Challenge Catalogue)

### Technical

- pgvector performance at scale (>10M vectors): benchmark early, have Qdrant as fallback
- Claude API cost at volume: estimate CHF 5K-15K/month at Phase 2 scale. Monitor closely.
- Multilingual NER quality for Swiss German: may need custom training data
- Real-time WebSocket scaling: evaluate Socket.IO vs native FastAPI WebSockets vs dedicated service
- PDF extraction quality for government reports: test multiple libraries (pymupdf, unstructured, docling)

### Legal

- Ancillary copyright timeline: could pass in 2026-2027. Budget for compliance.
- AI synthesis as "derivative work" argument: untested in Swiss courts. Get legal opinion.
- nDSG DPIA: commission from a qualified Swiss data protection consultant before launch.
- Source protection: establish formal editorial board with qualified journalists.

### Business

- Nau.ch partnership structure: JV vs investment vs technology license. Decision needed by Week 6.
- Wire service pricing: actual quotes needed from Keystone-SDA, AP, Reuters. Estimates may be off.
- Government agency B2G pipeline: validate willingness to pay (not just willingness to partner).
- Competitor response: TX Group, Ringier, or NZZ could build similar. Our moat is the knowledge
  graph + government data integration + speed of execution.
- Swiss audience skepticism toward AI-generated news: transparency and quality are the only answers.
  The trust indicators and source genome are not features — they're the product.

### Cultural

- Four-language parity: don't be a German-language product with French/Italian afterthoughts.
  Hire native speakers for editorial review in each language by Phase 2.
- Romandie and Ticino: these markets are underserved and will be especially receptive.
  Consider dedicated regional editors.
- Swiss precision expectations: one factual error in a synthesis = permanent reputation damage.
  Quality over speed, always.

---

## END OF CLAUDE.MD

This document is the single source of truth for the Signal.ch project.
When in doubt, refer to the legal constraints in §3 — they override everything else.
When building, follow the phase roadmap in §23 — it's ordered by dependency and legal safety.
When making design decisions, remember: we're building the Swiss Army knife of Swiss information.
Unlike the actual Swiss Army knife, people will use every single blade.

Let's build this.

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://signal-api.billowing-leaf-4d6a.workers.dev";

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("signal_token", token);
      } else {
        localStorage.removeItem("signal_token");
      }
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("signal_token");
    }
    return this.token;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_URL}/v1${path}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || `API error: ${res.status}`);
    }

    return res.json();
  }

  // Auth
  async register(data: { email: string; password: string; display_name?: string; preferred_language?: string }) {
    return this.request<{ access_token: string; user: User }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async login(email: string, password: string) {
    return this.request<{ access_token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async getMe() {
    return this.request<User>("/auth/me");
  }

  // IOs
  async listIOs(params: Record<string, string> = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request<IOListResponse>(`/ios?${query}`);
  }

  async getIO(id: string) {
    return this.request<IO>(`/ios/${id}`);
  }

  async getIOVersions(id: string) {
    return this.request<IOVersion[]>(`/ios/${id}/versions`);
  }

  async getIOSources(id: string) {
    return this.request<Source[]>(`/ios/${id}/sources`);
  }

  // Entities
  async listEntities(params: Record<string, string> = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request<EntityListResponse>(`/entities?${query}`);
  }

  async getEntity(id: string) {
    return this.request<Entity>(`/entities/${id}`);
  }

  async getEntityIOs(id: string) {
    return this.request<IO[]>(`/entities/${id}/ios`);
  }

  async getEntityRelations(id: string) {
    return this.request<EntityRelation[]>(`/entities/${id}/relations`);
  }

  // Search
  async search(q: string, params: Record<string, string> = {}) {
    const query = new URLSearchParams({ q, ...params }).toString();
    return this.request<IO[]>(`/search?${query}`);
  }

  // Votes
  async listVotes(params: Record<string, string> = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request<Vote[]>(`/votes?${query}`);
  }

  // Admin
  async getStats() {
    return this.request<DashboardStats>("/admin/stats");
  }

  async getReviewQueue(page = 1) {
    return this.request<{ items: ReviewItem[]; page: number }>(`/admin/review-queue?page=${page}`);
  }

  async reviewVersion(versionId: string, action: string, notes?: string) {
    return this.request(`/admin/review/${versionId}`, {
      method: "POST",
      body: JSON.stringify({ action, notes }),
    });
  }
}

export const api = new ApiClient();

// Types
export interface User {
  id: string;
  email: string;
  display_name: string | null;
  preferred_language: string;
  canton: string | null;
  tier: string;
  created_at: string;
}

export interface IOContent {
  title: string;
  lead: string;
  sections: { type: string; content: string; attributions?: string[] }[];
  summary: string;
}

export interface IOVersion {
  id: string;
  version_number: number;
  created_at: string;
  content_de: IOContent | null;
  content_fr: IOContent | null;
  content_it: IOContent | null;
  content_en: IOContent | null;
  trigger_type: string;
  review_status: string;
  diff_summary: Record<string, unknown> | null;
}

export interface IO {
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
  version_count: number;
  first_reported_at: string | null;
  current_version: IOVersion | null;
}

export interface IOListResponse {
  items: IO[];
  total: number;
  page: number;
  page_size: number;
}

export interface Source {
  id: string;
  source_type: string;
  license_status: string;
  original_url: string;
  original_title: string | null;
  original_language: string | null;
  original_published_at: string | null;
  snippet: string | null;
  attribution_text: string;
  author_name: string | null;
  publisher_reliability_score: number | null;
  contribution_type: string | null;
}

export interface Entity {
  id: string;
  entity_type: string;
  canonical_name: string;
  names_de: string[] | null;
  names_fr: string[] | null;
  names_it: string[] | null;
  names_en: string[] | null;
  aliases: string[] | null;
  metadata: Record<string, unknown>;
  wikidata_id: string | null;
  mention_count: number;
  last_mentioned_at: string | null;
}

export interface EntityListResponse {
  items: Entity[];
  total: number;
}

export interface EntityRelation {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  relation_type: string;
  confidence: number;
}

export interface Vote {
  id: string;
  vote_type: string;
  level: string;
  canton: string | null;
  title_de: string | null;
  title_fr: string | null;
  title_it: string | null;
  official_url: string | null;
  vote_date: string | null;
  status: string;
  pro_arguments: Record<string, unknown> | null;
  contra_arguments: Record<string, unknown> | null;
}

export interface DashboardStats {
  total_ios: number;
  published_ios: number;
  pending_reviews: number;
  total_sources: number;
  total_publishers: number;
  total_users: number;
}

export interface ReviewItem {
  version_id: string;
  io_id: string;
  version_number: number;
  trigger_type: string;
  created_at: string;
  content_de: IOContent | null;
  content_fr: IOContent | null;
  content_it: IOContent | null;
  content_en: IOContent | null;
  io_category: string;
  io_status: string;
}

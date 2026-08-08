/**
 * Bharat Vanguard News (BVN) — API Client
 * Typed wrapper around the FastAPI backend.
 * All functions return typed responses or throw errors.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================
//  TYPES
// ============================================================

export interface Publisher {
  publisher_id: string;
  name: string;
  slug: string;
  country?: string;
  logo_url?: string;
  reputation_score?: number;
  website?: string;
  is_official?: boolean;
}

export interface Article {
  article_id: string;
  title: string;
  slug: string;
  description?: string;
  content?: string;
  image_url?: string;
  author?: string;
  category?: string;
  country?: string;
  language?: string;
  published_time?: string;
  collected_time?: string;
  reading_time_min?: number;
  word_count?: number;
  url?: string;
  sentiment?: 'positive' | 'negative' | 'neutral' | 'mixed';
  publisher?: Publisher;
  confidence_score?: number;
  independent_sources?: number;
  cross_confirmation?: boolean;
  freshness_hours?: number;
  has_correction?: boolean;
  
  summary_short?: string;
  summary_medium?: string;
  summary_bullets?: string[];
  keywords?: string[];
  likes_count?: number;
}

export interface Event {
  event_id: string;
  title: string;
  slug: string;
  summary_short?: string;
  summary_medium?: string;
  summary_bullets?: string[];
  category?: string;
  country?: string;
  importance_score?: number;
  confidence_score?: number;
  sentiment?: string;
  article_count?: number;
  verified?: boolean;
  trending?: boolean;
  breaking?: boolean;
  first_seen?: string;
  last_updated?: string;
}

export interface ArticleInEvent extends Article {
  similarity_score?: number;
  is_primary?: boolean;
}

export interface EventDetail extends Event {
  articles: ArticleInEvent[];
  importance_score?: number;
  keywords?: string[];
}

export interface PaginatedEvents {
  items: Event[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface Entity {
  entity_id: string;
  name: string;
  slug: string;
  type: string;
  country?: string;
  description?: string;
  article_count?: number;
}

export interface PaginatedArticles {
  items: Article[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface SearchResponse {
  query: string;
  results: Article[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface AnalyticsSummary {
  total_articles: number;
  total_publishers: number;
  total_events: number;
  articles_today: number;
  articles_this_week: number;
  top_categories: Array<{ category: string; article_count: number; percentage: number }>;
  top_publishers: Array<{
    publisher_name: string;
    publisher_slug: string;
    article_count: number;
    country?: string;
    reputation_score?: number;
    logo_url?: string;
  }>;
  trending_entities: Array<{ entity_id: string; name: string; type: string; mention_count: number; country?: string }>;
  sentiment_breakdown: Array<{ sentiment: string; count: number; percentage: number }>;
}

export interface VolumePoint {
  date: string;
  count: number;
}

export interface SentimentStat {
  sentiment: string;
  count: number;
  percentage: number;
}

export interface TrendingEntity {
  entity_id: string;
  name: string;
  type: string;
  mention_count: number;
  country?: string;
}

export interface AuthUser {
  user_id: string;
  email: string;
  display_name?: string;
  username?: string;
  avatar_url?: string;
  role: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user?: AuthUser;
}

// ============================================================
//  FETCH HELPER
// ============================================================

type RequestOptions = RequestInit & {
  params?: Record<string, string | number | boolean | undefined>;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { params, ...fetchOptions } = options;

  let url = `${API_BASE}${path}`;

  if (params) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        query.set(k, String(v));
      }
    });
    const qs = query.toString();
    if (qs) url += `?${qs}`;
  }

  // Attach auth token if available (client-side only)
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string> || {}),
  };

  if (typeof window !== 'undefined') {
    try {
      const { createClient } = require('@/lib/supabase/client');
      const supabase = createClient();
      const { data } = await supabase.auth.getSession();
      if (data?.session?.access_token) {
        headers['Authorization'] = `Bearer ${data.session.access_token}`;
      }
    } catch (e) {
      // Fallback for non-browser environments or missing deps
      const token = localStorage.getItem('bvn_token');
      if (token) headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const finalFetchOptions: RequestInit = {
    ...fetchOptions,
    headers,
    next: { revalidate: 30 }, // Revalidate cache every 30 seconds for live news
  };

  const response = await fetch(url, finalFetchOptions);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ============================================================
//  ARTICLES
// ============================================================

export const articlesApi = {
  list: ({
    page = 1,
    page_size = 12,
    status = 'published',
    category,
    publisher_slug,
    country,
    language,
    sort_by,
  }: {
    page?: number;
    page_size?: number;
    status?: string;
    category?: string;
    publisher_slug?: string;
    country?: string;
    language?: string;
    sort_by?: 'published_time' | 'likes';
  }) => {
    const params: Record<string, any> = { page, page_size, status };
    if (category) params.category = category;
    if (publisher_slug) params.publisher_slug = publisher_slug;
    if (country) params.country = country;
    if (language) params.language = language;
    if (sort_by) params.sort_by = sort_by;
    return request<PaginatedArticles>('/api/v1/articles', { params });
  },

  get: (slug: string) => request<Article>(`/api/v1/articles/${slug}`),

  breaking: (limit = 6) =>
    request<Article[]>('/api/v1/articles/latest/breaking', { params: { limit } }),
};

// ============================================================
//  EVENTS
// ============================================================

export const eventsApi = {
  list: (params?: { page?: number; page_size?: number; category?: string; breaking?: boolean; trending?: boolean }) =>
    request<PaginatedEvents>('/api/v1/events', { params: params as any }),

  get: (slug: string) => request<EventDetail>(`/api/v1/events/${slug}`),

  trending: (limit = 8) =>
    request<Event[]>('/api/v1/events/trending', { params: { limit } }),

  breaking: (limit = 5) =>
    request<Event[]>('/api/v1/events/breaking', { params: { limit } }),
};

// ============================================================
//  PUBLISHERS
// ============================================================

export const publishersApi = {
  list: () => request<Publisher[]>('/api/v1/publishers'),
  get: (slug: string) => request<Publisher>(`/api/v1/publishers/${slug}`),
};

// ============================================================
//  ENTITIES
// ============================================================

export const entitiesApi = {
  list: (params?: { type?: string; page?: number; page_size?: number }) =>
    request<Entity[]>('/api/v1/entities', { params: params as any }),
  get: (slug: string) => request<Entity>(`/api/v1/entities/${slug}`),
};

// ============================================================
//  SEARCH
// ============================================================

export const searchApi = {
  search: (params: {
    q: string;
    page?: number;
    page_size?: number;
    category?: string;
    country?: string;
  }) => request<SearchResponse>('/api/v1/search', { params: params as any }),
};

// ============================================================
//  ANALYTICS
// ============================================================

export const analyticsApi = {
  summary: () => request<AnalyticsSummary>('/api/v1/analytics/summary'),
  categories: (days = 7) =>
    request<Array<{ category: string; article_count: number; percentage: number }>>(
      '/api/v1/analytics/categories', { params: { days } }
    ),
  countries: (days = 7) =>
    request<Array<{ country: string; count: number }>>('/api/v1/analytics/countries', { params: { days } }),
  volume: (days = 30, category?: string) =>
    request<VolumePoint[]>('/api/v1/analytics/volume', { params: { days, category } }),
  sentiment: (days = 7, category?: string) =>
    request<SentimentStat[]>('/api/v1/analytics/sentiment', { params: { days, category } }),
  trendingEntities: (days = 7, entity_type?: string, limit = 20) =>
    request<TrendingEntity[]>('/api/v1/analytics/trending-entities', {
      params: { days, entity_type, limit },
    }),
};

// ============================================================
//  MAGAZINES
// ============================================================

export const magazinesApi = {
  list: () => request<{ items: any[] }>('/api/v1/magazines'),
};

// ============================================================
//  AUTH
// ============================================================

export const authApi = {
  register: (data: { email: string; username: string; password: string; display_name?: string }) =>
    request<TokenResponse>('/api/v1/users/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.set('username', email);
    form.set('password', password);
    return request<TokenResponse>('/api/v1/users/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    });
  },

  me: () => request<AuthUser>('/api/v1/users/me'),

  googleUrl: () =>
    request<{ oauth_url: string }>('/api/v1/auth/google'),

  verifyGoogleToken: (access_token: string) =>
    request<TokenResponse>('/api/v1/auth/google/verify', {
      method: 'POST',
      body: JSON.stringify({ access_token }),
    }),

  getBookmarks: () => 
    request<{ bookmarked_article_ids: string[] }>('/api/v1/users/bookmarks/articles'),

  getBookmarkDetails: () => 
    request<{ items: any[] }>('/api/v1/users/bookmarks/details'),

  toggleBookmark: (article_id: string) => 
    request<{ status: string; article_id: string }>(`/api/v1/users/bookmarks/articles/${article_id}`, {
      method: 'POST',
    }),

  getLikes: () => 
    request<{ liked_article_ids: string[] }>('/api/v1/users/likes/articles'),

  toggleLike: (article_id: string) => 
    request<{ status: string; article_id: string }>(`/api/v1/users/likes/articles/${article_id}`, {
      method: 'POST',
    }),
};

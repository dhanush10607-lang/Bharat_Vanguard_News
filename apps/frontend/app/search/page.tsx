'use client';
import { useState, useCallback, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, X, SlidersHorizontal } from 'lucide-react';
import { searchApi } from '@/lib/api';
import { NewsCard, NewsCardSkeleton } from '@/components/news/NewsCard';
import { cn } from '@/lib/utils';

const CATEGORIES = ['', 'world', 'technology', 'ai', 'business', 'science', 'health', 'india', 'sports'];
const COUNTRIES   = ['', 'India', 'United States', 'United Kingdom', 'Global'];

function SearchPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [activeQuery, setActiveQuery] = useState(searchParams.get('q') || '');
  const [category, setCategory] = useState('');
  const [country, setCountry] = useState('');
  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['search', activeQuery, category, country, page],
    queryFn: () =>
      searchApi.search({ q: activeQuery, category: category || undefined, country: country || undefined, page }),
    enabled: activeQuery.length >= 2,
    placeholderData: (prev) => prev,
  });

  const handleSearch = useCallback(() => {
    if (query.trim().length < 2) return;
    setActiveQuery(query.trim());
    setPage(1);
    router.replace(`/search?q=${encodeURIComponent(query.trim())}`, { scroll: false });
  }, [query, router]);

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch();
  };

  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">

        {/* ── Search header ── */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-2">Search News</h1>
          <p className="text-text-muted">Search across {data?.total ? `${data.total.toLocaleString()} articles` : 'all articles'}</p>
        </div>

        {/* ── Search box ── */}
        <div className="flex gap-3 mb-4">
          <div className="relative flex-1">
            <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
            <input
              id="search-input"
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Search people, companies, topics, countries..."
              className="input pl-11 pr-4 py-3 text-base"
              autoFocus
            />
            {query && (
              <button
                onClick={() => { setQuery(''); setActiveQuery(''); }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
                aria-label="Clear search"
              >
                <X size={16} />
              </button>
            )}
          </div>
          <button
            id="search-btn"
            onClick={handleSearch}
            disabled={query.length < 2}
            className="btn-primary px-6 disabled:opacity-40"
          >
            Search
          </button>
          <button
            id="btn-filters"
            onClick={() => setShowFilters(!showFilters)}
            className={cn('btn-outline', showFilters && 'border-primary text-primary')}
            aria-label="Toggle filters"
          >
            <SlidersHorizontal size={16} />
          </button>
        </div>

        {/* ── Filters ── */}
        {showFilters && (
          <div className="flex flex-wrap gap-3 mb-6 p-4 bg-surface rounded-xl border border-border">
            <div className="flex flex-col gap-1 min-w-[140px]">
              <label className="text-2xs text-text-muted uppercase tracking-wider">Category</label>
              <select
                id="filter-category"
                value={category}
                onChange={(e) => { setCategory(e.target.value); setPage(1); }}
                className="input py-1.5 text-sm"
              >
                <option value="">All categories</option>
                {CATEGORIES.filter(Boolean).map((c) => (
                  <option key={c} value={c} className="bg-surface capitalize">{c}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1 min-w-[140px]">
              <label className="text-2xs text-text-muted uppercase tracking-wider">Country</label>
              <select
                id="filter-country"
                value={country}
                onChange={(e) => { setCountry(e.target.value); setPage(1); }}
                className="input py-1.5 text-sm"
              >
                <option value="">All countries</option>
                {COUNTRIES.filter(Boolean).map((c) => (
                  <option key={c} value={c} className="bg-surface">{c}</option>
                ))}
              </select>
            </div>
            {(category || country) && (
              <button
                onClick={() => { setCategory(''); setCountry(''); }}
                className="btn-ghost self-end text-xs text-rose-400"
              >
                <X size={12} /> Clear filters
              </button>
            )}
          </div>
        )}

        {/* ── Results ── */}
        {!activeQuery && (
          <div className="text-center py-20 text-text-muted">
            <Search size={48} className="mx-auto mb-4 opacity-20" />
            <p className="text-lg font-medium text-text-secondary">What would you like to know?</p>
            <p className="text-sm mt-2">Try searching "OpenAI", "India economy", "climate change"</p>
          </div>
        )}

        {activeQuery && isLoading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 9 }).map((_, i) => <NewsCardSkeleton key={i} />)}
          </div>
        )}

        {activeQuery && !isLoading && data && (
          <>
            <p className="text-sm text-text-muted mb-5">
              {data.total > 0
                ? `${data.total.toLocaleString()} results for "${activeQuery}"`
                : `No results for "${activeQuery}"`}
              {isFetching && <span className="ml-2 text-primary animate-pulse">Updating…</span>}
            </p>

            {data.results.length > 0 ? (
              <div className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4', isFetching && 'opacity-70')}>
                {data.results.map((article, i) => (
                  <NewsCard key={article.article_id} article={article} index={i} />
                ))}
              </div>
            ) : (
              <div className="text-center py-16 text-text-muted">
                <p>No articles matched your search.</p>
                <p className="text-sm mt-2">Try different keywords or remove filters.</p>
              </div>
            )}

            {/* Pagination */}
            {data.total > 20 && (
              <div className="flex items-center justify-center gap-3 mt-10">
                <button
                  id="search-prev-page"
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="btn-outline disabled:opacity-30"
                >
                  Previous
                </button>
                <span className="text-sm text-text-muted">Page {page}</span>
                <button
                  id="search-next-page"
                  onClick={() => setPage(page + 1)}
                  disabled={!data.has_next}
                  className="btn-outline disabled:opacity-30"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="pt-24 pb-16 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="skeleton h-8 w-48 rounded mb-6" />
          <div className="skeleton h-12 w-full rounded mb-4" />
        </div>
      </div>
    }>
      <SearchPageContent />
    </Suspense>
  );
}

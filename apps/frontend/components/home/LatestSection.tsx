'use client';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Clock, ArrowRight, Filter } from 'lucide-react';
import { articlesApi } from '@/lib/api';
import { NewsCard, NewsCardSkeleton } from '@/components/news/NewsCard';
import { cn } from '@/lib/utils';

const CATEGORIES = ['All', 'World', 'Technology', 'AI', 'Business', 'Science', 'Health', 'India', 'Sports'];

export function LatestSection() {
  const [activeCategory, setActiveCategory] = useState('All');
  const [page, setPage] = useState(1);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['articles', 'latest', activeCategory, page],
    queryFn: () =>
      articlesApi.list({
        page,
        page_size: 9,
        status: 'published',
        category: activeCategory === 'All' ? undefined : activeCategory.toLowerCase(),
      }),
    placeholderData: (prev) => prev,
  });

  const handleCategory = (cat: string) => {
    setActiveCategory(cat);
    setPage(1);
  };

  return (
    <div>
      {/* Section header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald/10">
            <Clock size={16} className="text-emerald" />
          </div>
          <div>
            <h2 className="section-title">Latest Articles</h2>
            <p className="text-xs text-text-muted">
              {data?.total ? `${data.total.toLocaleString()} articles` : 'Collecting...'}
            </p>
          </div>
        </div>
      </div>

      {/* Category filter pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-3 mb-5 scrollbar-none">
        <Filter size={13} className="text-text-muted shrink-0" />
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            id={`filter-${cat.toLowerCase()}`}
            onClick={() => handleCategory(cat)}
            className={cn(
              'px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-200',
              activeCategory === cat
                ? 'bg-primary text-white shadow-glow-blue'
                : 'bg-surface-2 text-text-muted hover:text-text-primary hover:bg-border'
            )}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Articles grid */}
      <div className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4', isFetching && 'opacity-70 transition-opacity')}>
        {isLoading ? (
          Array.from({ length: 9 }).map((_, i) => <NewsCardSkeleton key={i} />)
        ) : (
          (data?.items || []).map((article, i) => (
            <NewsCard key={article.article_id} article={article} index={i} />
          ))
        )}
      </div>

      {/* Empty state */}
      {!isLoading && !data?.items?.length && (
        <div className="text-center py-16 text-text-muted">
          <Clock size={32} className="mx-auto mb-3 opacity-30" />
          <p className="font-medium">No articles yet</p>
          <p className="text-sm mt-1">Run the RSS collector to populate news</p>
        </div>
      )}

      {/* Pagination */}
      {data && data.total > 9 && (
        <div className="flex items-center justify-center gap-3 mt-8">
          <button
            id="btn-prev-page"
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="btn-outline disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-sm text-text-muted">
            Page {page} of {Math.ceil(data.total / 9)}
          </span>
          <button
            id="btn-next-page"
            onClick={() => setPage(page + 1)}
            disabled={!data.has_next}
            className="btn-outline disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Next <ArrowRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}

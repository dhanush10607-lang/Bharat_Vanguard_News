'use client';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { articlesApi } from '@/lib/api';
import { NewsCard, NewsCardSkeleton } from '@/components/news/NewsCard';
import { ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

export function CategoryFeed({ category }: { category: string }) {
  const [page, setPage] = useState(1);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['articles', 'category', category, page],
    queryFn: () => articlesApi.list({ category, page, page_size: 12, status: 'published' }),
    placeholderData: (prev) => prev,
  });

  return (
    <div>
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 12 }).map((_, i) => <NewsCardSkeleton key={i} />)}
        </div>
      ) : (
        <>
          {data?.total != null && (
            <p className="text-sm text-text-muted mb-5">
              {data.total.toLocaleString()} articles
            </p>
          )}
          <div className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4', isFetching && 'opacity-70')}>
            {(data?.items || []).map((article, i) => (
              <NewsCard key={article.article_id} article={article} index={i} />
            ))}
          </div>

          {!data?.items?.length && (
            <div className="text-center py-20 text-text-muted">
              <p>No articles in this category yet.</p>
              <p className="text-sm mt-1">Run the collector to populate news.</p>
            </div>
          )}

          {data && data.total > 12 && (
            <div className="flex items-center justify-center gap-3 mt-10">
              <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="btn-outline disabled:opacity-30">Previous</button>
              <span className="text-sm text-text-muted">Page {page} of {Math.ceil(data.total / 12)}</span>
              <button onClick={() => setPage(page + 1)} disabled={!data.has_next} className="btn-outline disabled:opacity-30">Next <ArrowRight size={14} /></button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

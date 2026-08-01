'use client';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { TrendingUp, ArrowRight } from 'lucide-react';
import { articlesApi } from '@/lib/api';
import { NewsCard, NewsCardSkeleton } from '@/components/news/NewsCard';

export function TrendingSection() {
  const { data, isLoading } = useQuery({
    queryKey: ['articles', 'trending'],
    queryFn: () => articlesApi.list({ page: 1, page_size: 4, status: 'published' }),
  });

  return (
    <div>
      {/* Section header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10">
            <TrendingUp size={16} className="text-primary" />
          </div>
          <div>
            <h2 className="section-title">Trending Now</h2>
            <p className="text-xs text-text-muted">Most discussed stories</p>
          </div>
        </div>
        <Link href="/search" className="btn-ghost text-xs">
          View all <ArrowRight size={13} />
        </Link>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <NewsCardSkeleton key={i} />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
          {(data?.items || []).map((article, i) => (
            <NewsCard key={article.article_id} article={article} index={i} compact />
          ))}
        </div>
      )}
    </div>
  );
}

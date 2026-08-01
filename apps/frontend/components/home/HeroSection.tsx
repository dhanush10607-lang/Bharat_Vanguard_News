'use client';
import { useQuery } from '@tanstack/react-query';
import { articlesApi } from '@/lib/api';
import { HeroCard } from '@/components/news/NewsCard';
import { NewsCard, NewsCardSkeleton } from '@/components/news/NewsCard';

export function HeroSection() {
  const { data, isLoading } = useQuery({
    queryKey: ['breaking'],
    queryFn: () => articlesApi.breaking(6),
  });

  if (isLoading) {
    return <div className="skeleton rounded-3xl" style={{ height: 420 }} />;
  }

  const articles = data || [];
  if (articles.length === 0) return null;

  const [hero, ...rest] = articles;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Main hero */}
      <div className="lg:col-span-2">
        <HeroCard article={hero} />
      </div>

      {/* Side cards */}
      <div className="flex flex-col gap-3">
        {rest.slice(0, 3).map((article, i) => (
          <NewsCard key={article.article_id} article={article} index={i} compact />
        ))}
      </div>
    </div>
  );
}

import type { Metadata } from 'next';
import { Suspense } from 'react';
import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { HeroSection } from '@/components/home/HeroSection';
import { TrendingSection } from '@/components/home/TrendingSection';
import { LatestSection } from '@/components/home/LatestSection';
import { CategoryNav } from '@/components/home/CategoryNav';
import { BreakingTicker } from '@/components/home/BreakingTicker';
import { PodcastPlayer } from '@/components/home/PodcastPlayer';
import { articlesApi } from '@/lib/api';

export const metadata: Metadata = {
  title: 'Bharat Vanguard News (BVN) — India\'s AI-Powered News Platform',
  description:
    'Real-time news from trusted sources. AI-analyzed, verified with transparent trust scores. Search, explore and understand the news.',
};

export default async function HomePage() {
  const queryClient = new QueryClient();

  // Prefetch Latest Articles (First Page, All Categories)
  await queryClient.prefetchQuery({
    queryKey: ['articles', 'latest', 'All', 1],
    queryFn: () => articlesApi.list({ page: 1, page_size: 9, status: 'published' }),
  });

  // (Optional) Prefetch Trending or other critical sections here

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <div className="pb-16">
        
        {/* Breaking News Ticker */}
        <Suspense fallback={null}>
          <BreakingTicker />
        </Suspense>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 space-y-12">
          
          {/* Hero Section */}
          <section className="pt-8">
            <Suspense fallback={<div className="skeleton rounded-3xl" style={{ height: 420 }} />}>
              <HeroSection />
            </Suspense>
          </section>

          {/* Podcast Player */}
          <section>
            <PodcastPlayer />
          </section>

          {/* Category quick-nav */}
          <section>
            <CategoryNav />
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
            {/* Main Content Area: Top Stories & Latest */}
            <div className="lg:col-span-2 space-y-12">
              <section>
                <Suspense fallback={<div className="skeleton h-96 rounded-xl" />}>
                  <LatestSection />
                </Suspense>
              </section>
            </div>

            {/* Sidebar: Trending & Newsletter */}
            <aside className="space-y-12">
              <section>
                <Suspense fallback={<div className="skeleton h-96 rounded-xl" />}>
                  <TrendingSection />
                </Suspense>
              </section>
            </aside>
          </div>
          
        </div>
      </div>
    </HydrationBoundary>
  );
}

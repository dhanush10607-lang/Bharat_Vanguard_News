import type { Metadata } from 'next';
import { Suspense } from 'react';
import { HeroSection } from '@/components/home/HeroSection';
import { TrendingSection } from '@/components/home/TrendingSection';
import { LatestSection } from '@/components/home/LatestSection';
import { StatsBar } from '@/components/home/StatsBar';
import { CategoryNav } from '@/components/home/CategoryNav';

export const metadata: Metadata = {
  title: 'Bharat Vanguard News (BVN) — India\'s AI-Powered News Platform',
  description:
    'Real-time news from trusted sources. AI-analyzed, verified with transparent trust scores. Search, explore and understand the news.',
};

export default function HomePage() {
  return (
    <div className="pt-16">
      {/* Stats bar */}
      <Suspense fallback={null}>
        <StatsBar />
      </Suspense>

      {/* Hero — Breaking news */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pt-6">
        <Suspense fallback={<div className="skeleton rounded-3xl" style={{ height: 420 }} />}>
          <HeroSection />
        </Suspense>
      </section>

      {/* Category quick-nav */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pt-8">
        <CategoryNav />
      </section>

      {/* Trending stories */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pt-10">
        <Suspense fallback={null}>
          <TrendingSection />
        </Suspense>
      </section>

      {/* Latest articles */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pt-10 pb-16">
        <Suspense fallback={null}>
          <LatestSection />
        </Suspense>
      </section>
    </div>
  );
}

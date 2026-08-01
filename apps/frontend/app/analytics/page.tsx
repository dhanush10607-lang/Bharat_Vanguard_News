import type { Metadata } from 'next';
import { Suspense } from 'react';
import { AnalyticsDashboard } from '@/components/analytics/AnalyticsDashboard';

export const metadata: Metadata = {
  title: 'Analytics — TruthLens AI',
  description: 'Real-time news analytics — trending topics, sentiment analysis, source distribution, and article volume charts.',
};

export default function AnalyticsPage() {
  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-1.5">Analytics</h1>
          <p className="text-text-muted">Real-time insights across all collected news</p>
        </div>
        <Suspense fallback={null}>
          <AnalyticsDashboard />
        </Suspense>
      </div>
    </div>
  );
}

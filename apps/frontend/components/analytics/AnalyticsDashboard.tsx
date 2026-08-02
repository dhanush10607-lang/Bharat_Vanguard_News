'use client';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi, type AnalyticsSummary } from '@/lib/api';
import { motion } from 'framer-motion';
import {
  FileText, Globe, Zap, Calendar, TrendingUp, Users,
  Shield, BarChart3, PieChart, Activity, User, Building2, MapPin
} from 'lucide-react';
import { cn, capitalize, getSentimentClass, formatScore } from '@/lib/utils';

// ============================================================
//  MINI CHART — Bar chart built purely in CSS/SVG (no dependencies)
// ============================================================

function BarMini({ values, color = '#3B82F6', height = 48 }: {
  values: number[];
  color?: string;
  height?: number;
}) {
  if (!values.length) return null;
  const max = Math.max(...values, 1);
  return (
    <div className="flex items-end gap-0.5" style={{ height }}>
      {values.map((v, i) => (
        <motion.div
          key={i}
          initial={{ scaleY: 0 }}
          animate={{ scaleY: 1 }}
          transition={{ delay: i * 0.02, duration: 0.4 }}
          style={{
            height: `${(v / max) * 100}%`,
            backgroundColor: color,
            flex: 1,
            borderRadius: 2,
            transformOrigin: 'bottom',
            opacity: 0.7 + (v / max) * 0.3,
          }}
        />
      ))}
    </div>
  );
}

// ============================================================
//  STAT CARD
// ============================================================

function StatCard({ icon, label, value, sub, color }: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
  color: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-5"
    >
      <div className="flex items-start justify-between mb-3">
        <div className={cn('p-2 rounded-lg', color)}>{icon}</div>
      </div>
      <p className="text-2xl font-bold text-text-primary">{value}</p>
      <p className="text-sm text-text-muted mt-0.5">{label}</p>
      {sub && <p className="text-xs text-text-muted/60 mt-1">{sub}</p>}
    </motion.div>
  );
}

// ============================================================
//  ENTITY TYPE ICON
// ============================================================
function EntityIcon({ type }: { type: string }) {
  switch (type) {
    case 'person':       return <User size={13} className="text-blue-400" />;
    case 'organization': return <Building2 size={13} className="text-violet-400" />;
    case 'location':
    case 'country':      return <MapPin size={13} className="text-emerald-400" />;
    default:             return <Globe size={13} className="text-text-muted" />;
  }
}

// ============================================================
//  SENTIMENT BADGE
// ============================================================

const SENTIMENT_COLOR: Record<string, string> = {
  positive: 'bg-green-500/15 text-green-500 border-green-500/30',
  negative: 'bg-red-500/15 text-red-500 border-red-500/30',
  neutral:  'bg-text-muted/10 text-text-muted border-border',
  mixed:    'bg-amber/15 text-amber border-amber/30',
};

// ============================================================
//  MAIN DASHBOARD
// ============================================================

export function AnalyticsDashboard() {
  const [days, setDays] = useState(7);

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['analytics', 'summary'],
    queryFn: analyticsApi.summary,
    staleTime: 2 * 60 * 1000,
  });

  const { data: volumeData } = useQuery({
    queryKey: ['analytics', 'volume', 30],
    queryFn: () => analyticsApi.volume(30),
    staleTime: 5 * 60 * 1000,
  });

  const { data: entitiesData } = useQuery({
    queryKey: ['analytics', 'entities', days],
    queryFn: () => analyticsApi.trendingEntities(days, undefined, 20),
    staleTime: 3 * 60 * 1000,
  });

  if (summaryLoading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="card p-5 h-28 skeleton" />
        ))}
      </div>
    );
  }

  const s = summary!;
  const volumeValues = volumeData?.map(v => v.count) || [];

  return (
    <div className="space-y-8">
      {/* ── Key Stats ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={<FileText size={16} className="text-primary" />}   label="Total Articles"  value={s.total_articles.toLocaleString()}  color="bg-primary/10" />
        <StatCard icon={<Globe size={16} className="text-emerald" />}      label="Publishers"      value={s.total_publishers}                  color="bg-emerald/10" />
        <StatCard icon={<Zap size={16} className="text-amber" />}          label="Events"          value={s.total_events.toLocaleString()}      color="bg-amber/10" />
        <StatCard icon={<Calendar size={16} className="text-violet-400" />} label="Today"          value={s.articles_today.toLocaleString()}    sub="Last 24 hours" color="bg-violet-400/10" />
      </div>

      {/* ── Volume chart + Sentiment ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* Volume chart */}
        <div className="card p-5 lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <Activity size={16} className="text-primary" />
            <h2 className="text-sm font-semibold text-text-primary">Article Volume (30 days)</h2>
          </div>
          {volumeValues.length > 0 ? (
            <>
              <BarMini values={volumeValues} height={80} />
              <div className="flex justify-between mt-2">
                <span className="text-2xs text-text-muted">{volumeData![0]?.date}</span>
                <span className="text-2xs text-text-muted">{volumeData![volumeData!.length - 1]?.date}</span>
              </div>
            </>
          ) : (
            <div className="h-20 flex items-center justify-center text-text-muted text-sm">
              No volume data yet
            </div>
          )}
        </div>

        {/* Sentiment breakdown */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <PieChart size={16} className="text-primary" />
            <h2 className="text-sm font-semibold text-text-primary">Sentiment</h2>
          </div>
          <div className="space-y-2.5">
            {(s.sentiment_breakdown || []).map((item) => (
              <div key={item.sentiment}>
                <div className="flex justify-between text-xs mb-1">
                  <span className={cn(
                    'capitalize font-medium',
                    item.sentiment === 'positive' ? 'text-green-500' :
                    item.sentiment === 'negative' ? 'text-red-500' :
                    item.sentiment === 'mixed' ? 'text-amber' : 'text-text-muted'
                  )}>
                    {item.sentiment}
                  </span>
                  <span className="text-text-muted">{item.percentage}%</span>
                </div>
                <div className="w-full h-1.5 bg-surface-2 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.percentage}%` }}
                    transition={{ duration: 0.6, ease: 'easeOut' }}
                    className={cn('h-full rounded-full',
                      item.sentiment === 'positive' ? 'bg-green-500' :
                      item.sentiment === 'negative' ? 'bg-red-500' :
                      item.sentiment === 'mixed' ? 'bg-amber' : 'bg-text-muted/50'
                    )}
                  />
                </div>
              </div>
            ))}
            {!s.sentiment_breakdown?.length && (
              <p className="text-sm text-text-muted text-center py-4">No sentiment data yet</p>
            )}
          </div>
        </div>
      </div>

      {/* ── Categories + Publishers ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        {/* Top categories */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 size={16} className="text-primary" />
            <h2 className="text-sm font-semibold text-text-primary">Top Categories</h2>
          </div>
          <div className="space-y-3">
            {s.top_categories.slice(0, 8).map((cat, i) => (
              <motion.div
                key={cat.category}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="flex justify-between text-xs mb-1">
                  <span className="capitalize text-text-secondary font-medium">{cat.category}</span>
                  <span className="text-text-muted">{cat.article_count.toLocaleString()}</span>
                </div>
                <div className="w-full h-1.5 bg-surface-2 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${cat.percentage}%` }}
                    transition={{ duration: 0.5, delay: i * 0.05 }}
                    className="h-full rounded-full bg-primary"
                    style={{ opacity: 1 - i * 0.07 }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Top publishers */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <Globe size={16} className="text-primary" />
            <h2 className="text-sm font-semibold text-text-primary">Top Publishers</h2>
          </div>
          <div className="space-y-2.5">
            {s.top_publishers.slice(0, 8).map((pub, i) => (
              <motion.div
                key={pub.publisher_slug}
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                className="flex items-center justify-between"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-xs text-text-muted w-4 shrink-0">{i + 1}</span>
                  <div className="w-5 h-5 rounded bg-surface-2 flex items-center justify-center shrink-0 overflow-hidden">
                    {pub.logo_url ? (
                      <img src={pub.logo_url} alt={pub.publisher_name} className="w-5 h-5 object-contain" />
                    ) : (
                      <Globe size={10} className="text-text-muted" />
                    )}
                  </div>
                  <span className="text-xs text-text-primary font-medium truncate">{pub.publisher_name}</span>
                  {pub.country && (
                    <span className="text-2xs text-text-muted hidden sm:block">{pub.country}</span>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {pub.reputation_score != null && (
                    <span className="text-2xs text-emerald font-medium">{Math.round(pub.reputation_score * 100)}%</span>
                  )}
                  <span className="text-xs text-text-muted tabular-nums">{pub.article_count.toLocaleString()}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Trending Entities ── */}
      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp size={16} className="text-primary" />
            <h2 className="text-sm font-semibold text-text-primary">Trending Entities</h2>
          </div>
          {/* Time filter */}
          <div className="flex items-center gap-1">
            {[3, 7, 14, 30].map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={cn(
                  'px-2 py-0.5 rounded text-xs transition-colors',
                  days === d ? 'bg-primary text-white' : 'text-text-muted hover:text-text-primary'
                )}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>

        {!entitiesData?.length ? (
          <p className="text-sm text-text-muted text-center py-8">
            Trending entities appear here after the NLP pipeline processes articles.
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
            {(entitiesData || []).slice(0, 20).map((ent, i) => (
              <motion.div
                key={ent.entity_id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.03 }}
                className="flex items-center gap-2 px-3 py-2.5 rounded-xl bg-surface-2 border border-border hover:border-border-2 transition-all"
              >
                <EntityIcon type={ent.type} />
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-text-primary truncate">{ent.name}</p>
                  <p className="text-2xs text-text-muted capitalize">{ent.type} · {ent.mention_count} mentions</p>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

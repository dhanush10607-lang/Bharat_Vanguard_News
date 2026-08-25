'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/lib/api';
import { motion } from 'framer-motion';
import {
  FileText, Globe, Zap, Calendar, TrendingUp,
  BarChart3, Activity, User, Building2, MapPin,
  PieChart as PieChartIcon
} from 'lucide-react';
import { cn, capitalize } from '@/lib/utils';
import {
  BarChart, Bar, ResponsiveContainer, Tooltip, XAxis, YAxis,
  PieChart, Pie, Cell, CartesianGrid
} from 'recharts';

// ============================================================
//  STAT CARD
// ============================================================

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
  color: string;
}

function StatCard({ icon, label, value, sub, color }: StatCardProps) {
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
//  COLORS FOR RECHARTS
// ============================================================
const SENTIMENT_COLORS: Record<string, string> = {
  positive: '#22c55e',
  negative: '#ef4444',
  mixed: '#f59e0b',
  neutral: '#737373',
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

  if (summaryLoading || !summary) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="card p-5 h-28 skeleton" />
        ))}
      </div>
    );
  }

  const s = summary;

  // Format data for Recharts
  const formattedVolumeData = (volumeData || []).map((v) => ({
    name: new Date(v.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    count: v.count,
  }));

  const sentimentData = (s.sentiment_breakdown || []).map((item) => ({
    name: capitalize(item.sentiment.toLowerCase()),
    value: item.percentage,
    color: SENTIMENT_COLORS[item.sentiment.toLowerCase()] || '#8884d8'
  }));

  const categoryData = (s.top_categories || []).slice(0, 8).map((cat) => ({
    name: capitalize(cat.category),
    value: cat.article_count,
  }));

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
        <div className="card p-5 lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <Activity size={16} className="text-primary" />
            <h2 className="text-sm font-semibold text-text-primary">Article Volume (30 days)</h2>
          </div>
          {formattedVolumeData.length > 0 ? (
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={formattedVolumeData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                  <Tooltip 
                    cursor={{fill: 'rgba(255,255,255,0.05)'}}
                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  />
                  <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-20 flex items-center justify-center text-text-muted text-sm">
              No volume data yet
            </div>
          )}
        </div>

        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <PieChartIcon size={16} className="text-primary" />
            <h2 className="text-sm font-semibold text-text-primary">Sentiment Analysis</h2>
          </div>
          <div className="h-64 w-full flex items-center justify-center relative">
            {sentimentData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Percentage']}
                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-text-muted text-center">No sentiment data</p>
            )}
            
            {sentimentData.length > 0 && (
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-2xl font-bold text-text-primary">
                  {sentimentData.find(s => s.name === 'Positive')?.value || 0}%
                </span>
                <span className="text-xs text-text-muted">Positive</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Categories + Publishers ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 size={16} className="text-primary" />
            <h2 className="text-sm font-semibold text-text-primary">Top Categories</h2>
          </div>
          <div className="h-64 w-full">
             <ResponsiveContainer width="100%" height="100%">
               <BarChart data={categoryData} layout="vertical" margin={{ top: 0, right: 0, left: 20, bottom: 0 }}>
                 <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="rgba(255,255,255,0.05)" />
                 <XAxis type="number" hide />
                 <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#888888', fontSize: 12}} />
                 <Tooltip 
                    cursor={{fill: 'rgba(255,255,255,0.05)'}}
                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  />
                 <Bar dataKey="value" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={20} />
               </BarChart>
             </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <Globe size={16} className="text-primary" />
            <h2 className="text-sm font-semibold text-text-primary">Top Publishers</h2>
          </div>
          <div className="space-y-2.5 mt-4">
            {s.top_publishers.slice(0, 7).map((pub, i) => (
              <motion.div
                key={pub.publisher_slug}
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                className="flex items-center justify-between"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-xs text-text-muted w-4 shrink-0">{i + 1}</span>
                  <div className="w-6 h-6 rounded bg-surface-2 flex items-center justify-center shrink-0 overflow-hidden border border-border">
                    {pub.logo_url ? (
                      <img src={pub.logo_url} alt={pub.publisher_name} className="w-4 h-4 object-contain" />
                    ) : (
                      <Globe size={12} className="text-text-muted" />
                    )}
                  </div>
                  <span className="text-sm text-text-primary font-medium truncate">{pub.publisher_name}</span>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-xs text-text-muted tabular-nums bg-surface-2 px-2 py-0.5 rounded-full">
                    {pub.article_count.toLocaleString()} articles
                  </span>
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
          <div className="flex items-center gap-1 bg-surface-2 p-1 rounded-lg">
            {[3, 7, 14, 30].map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={cn(
                  'px-3 py-1 rounded-md text-xs font-medium transition-all',
                  days === d ? 'bg-primary text-white shadow-sm' : 'text-text-muted hover:text-text-primary'
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
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
            {(entitiesData || []).slice(0, 20).map((ent, i) => (
              <motion.div
                key={ent.entity_id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.02 }}
                className="flex items-center gap-3 px-4 py-3 rounded-xl bg-surface border border-border/50 hover:border-primary/30 hover:bg-surface-2 transition-all group"
              >
                <div className="p-2 rounded-lg bg-surface-2 group-hover:bg-surface-3 transition-colors">
                  <EntityIcon type={ent.type} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-text-primary truncate">{ent.name}</p>
                  <p className="text-xs text-text-muted mt-0.5 capitalize flex justify-between">
                    <span>{ent.type}</span>
                    <span className="text-primary-light font-medium">{ent.mention_count}</span>
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

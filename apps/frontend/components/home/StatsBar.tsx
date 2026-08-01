'use client';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/lib/api';
import { FileText, Globe, Zap, Calendar } from 'lucide-react';

export function StatsBar() {
  const { data } = useQuery({
    queryKey: ['analytics', 'summary'],
    queryFn: analyticsApi.summary,
    staleTime: 5 * 60 * 1000,
  });

  const stats = [
    { icon: <FileText size={14} />, value: data?.total_articles?.toLocaleString() ?? '—', label: 'Articles' },
    { icon: <Globe size={14} />,    value: data?.total_publishers?.toString() ?? '—',    label: 'Publishers' },
    { icon: <Calendar size={14} />, value: data?.articles_today?.toLocaleString() ?? '—', label: 'Today' },
    { icon: <Zap size={14} />,      value: data?.articles_this_week?.toLocaleString() ?? '—', label: 'This Week' },
  ];

  return (
    <div className="border-b border-border bg-surface/50 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-2.5">
        <div className="flex items-center gap-6 overflow-x-auto scrollbar-none">
          {/* Live indicator */}
          <div className="flex items-center gap-1.5 shrink-0">
            <span className="dot-live" />
            <span className="text-xs font-medium text-text-secondary">LIVE</span>
          </div>

          <div className="h-4 w-px bg-border shrink-0" />

          {/* Stats */}
          {stats.map((s) => (
            <div key={s.label} className="flex items-center gap-1.5 shrink-0">
              <span className="text-text-muted">{s.icon}</span>
              <span className="text-xs font-bold text-text-primary">{s.value}</span>
              <span className="text-xs text-text-muted">{s.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

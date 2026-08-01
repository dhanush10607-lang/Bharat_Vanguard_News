'use client';
import { Shield, CheckCircle, AlertCircle, Clock, Users, Star, RefreshCw, Info } from 'lucide-react';
import { cn, getTrustClass, getTrustLabel, formatScore, formatDateTime } from '@/lib/utils';
import { motion } from 'framer-motion';
import Link from 'next/link';

interface TrustSignalData {
  confidence_score?: number | null;
  official_source?: boolean;
  independent_sources?: number;
  publisher_reputation?: number;
  cross_confirmation?: boolean;
  has_correction?: boolean;
  freshness_hours?: number;
  last_checked?: string;
  signal_breakdown?: {
    official_source?: number;
    independent_sources?: number;
    publisher_reputation?: number;
    cross_confirmation?: number;
    freshness?: number;
  };
}

interface TrustScoreProps {
  data: TrustSignalData;
  compact?: boolean;
}

export function TrustScore({ data, compact = false }: TrustScoreProps) {
  const score = data.confidence_score;
  const pct = score != null ? Math.round(score * 100) : null;

  if (compact) {
    return (
      <div className="flex items-center gap-1.5">
        <Shield size={13} className={getTrustClass(score)} />
        <span className={cn('text-sm font-semibold', getTrustClass(score))}>
          {pct != null ? `${pct}%` : '—'}
        </span>
        <span className="text-xs text-text-muted">{getTrustLabel(score)}</span>
      </div>
    );
  }

  return (
    <div className="card p-5">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-1.5 mb-0.5">
            <h3 className="text-sm font-semibold text-text-primary">Evidence Strength</h3>
            <Link href="/methodology" className="text-text-muted hover:text-primary transition-colors" title="View Methodology">
              <Info size={14} />
            </Link>
          </div>
          <p className="text-2xs text-text-muted">
            Based on verifiable signals — not a fact-check verdict
          </p>
        </div>
        <div className="text-right">
          <span className={cn('text-3xl font-bold', getTrustClass(score))}>
            {pct != null ? `${pct}%` : '—'}
          </span>
          <p className={cn('text-xs font-medium mt-0.5', getTrustClass(score))}>
            {getTrustLabel(score)}
          </p>
        </div>
      </div>

      {/* Progress bar */}
      {pct != null && (
        <div className="w-full h-2 bg-surface-2 rounded-full overflow-hidden mb-4">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={cn(
              'h-full rounded-full',
              pct >= 70 ? 'bg-emerald' : pct >= 40 ? 'bg-amber' : 'bg-rose'
            )}
          />
        </div>
      )}

      {/* Signal breakdown */}
      <div className="space-y-2.5">
        <SignalRow
          icon={<Star size={13} />}
          label="Official source"
          value={data.official_source}
          type="boolean"
        />
        <SignalRow
          icon={<Users size={13} />}
          label="Independent sources"
          value={data.independent_sources}
          type="count"
          suffix="publishers"
        />
        <SignalRow
          icon={<Shield size={13} />}
          label="Publisher reputation"
          value={data.publisher_reputation}
          type="score"
        />
        <SignalRow
          icon={<CheckCircle size={13} />}
          label="Cross-source agreement"
          value={data.cross_confirmation}
          type="boolean"
        />
        <SignalRow
          icon={<Clock size={13} />}
          label="Information freshness"
          value={data.freshness_hours != null ? (data.freshness_hours <= 24) : undefined}
          type="boolean"
          trueLabel={data.freshness_hours != null ? `${Math.round(data.freshness_hours)}h ago` : 'Recent'}
          falseLabel={data.freshness_hours != null ? `${Math.round(data.freshness_hours)}h ago` : 'Older'}
        />
        {data.has_correction && (
          <div className="flex items-center gap-2 text-xs text-amber">
            <AlertCircle size={13} />
            <span>Correction has been issued</span>
          </div>
        )}
      </div>

      {/* Last checked */}
      {data.last_checked && (
        <div className="flex items-center gap-1.5 mt-4 pt-3 border-t border-border">
          <RefreshCw size={11} className="text-text-muted" />
          <span className="text-2xs text-text-muted">
            Last verified {formatDateTime(data.last_checked)}
          </span>
        </div>
      )}
    </div>
  );
}

// ── Individual signal row ──
function SignalRow({
  icon,
  label,
  value,
  type,
  suffix,
  trueLabel = 'Yes',
  falseLabel = 'No',
}: {
  icon: React.ReactNode;
  label: string;
  value: boolean | number | undefined;
  type: 'boolean' | 'count' | 'score';
  suffix?: string;
  trueLabel?: string;
  falseLabel?: string;
}) {
  const getDisplay = () => {
    if (value === undefined || value === null) return { text: 'Unknown', className: 'text-text-muted' };
    if (type === 'boolean') {
      return value
        ? { text: trueLabel, className: 'text-emerald' }
        : { text: falseLabel, className: 'text-text-muted' };
    }
    if (type === 'count') {
      const n = value as number;
      return {
        text: `${n} ${suffix || ''}`,
        className: n >= 5 ? 'text-emerald' : n >= 2 ? 'text-amber' : 'text-text-muted',
      };
    }
    if (type === 'score') {
      const s = value as number;
      return {
        text: `${Math.round(s * 100)}%`,
        className: s >= 0.7 ? 'text-emerald' : s >= 0.4 ? 'text-amber' : 'text-rose',
      };
    }
    return { text: String(value), className: 'text-text-muted' };
  };

  const { text, className } = getDisplay();

  return (
    <div className="flex items-center justify-between gap-2">
      <div className="flex items-center gap-2 text-text-muted">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <span className={cn('text-xs font-semibold', className)}>{text}</span>
    </div>
  );
}

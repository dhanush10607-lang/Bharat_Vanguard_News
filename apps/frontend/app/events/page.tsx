'use client';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Users, Clock, Shield, ArrowRight, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { eventsApi } from '@/lib/api';
import { cn, formatRelative, getCategoryBadgeClass, getTrustClass, formatScore } from '@/lib/utils';

export default function EventsPage() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['events', page],
    queryFn: () => eventsApi.list({ page, page_size: 15 }),
    placeholderData: (prev) => prev,
  });

  return (
    <div className="pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-1.5">Events</h1>
          <p className="text-text-muted">Grouped stories from multiple publishers</p>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="card p-5 h-24 skeleton" />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {(data?.items || []).map((event, i) => (
              <motion.article
                key={event.event_id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className="card p-5 group"
              >
                <Link href={`/events/${event.slug}`} className="flex flex-col sm:flex-row sm:items-start gap-4">
                  <div className="flex-1 min-w-0">
                    {/* Badges */}
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      {event.breaking && (
                        <span className="flex items-center gap-1 text-xs text-rose-400 font-semibold">
                          <span className="dot-live" />BREAKING
                        </span>
                      )}
                      {event.category && (
                        <span className={getCategoryBadgeClass(event.category)}>{event.category}</span>
                      )}
                    </div>

                    {/* Title */}
                    <h2 className="text-base font-bold text-text-primary group-hover:text-primary-light transition-colors line-clamp-2 mb-2">
                      {event.title}
                    </h2>

                    {/* Summary */}
                    {event.summary_short && (
                      <p className="text-sm text-text-muted line-clamp-1">{event.summary_short}</p>
                    )}

                    {/* Meta */}
                    <div className="flex flex-wrap items-center gap-3 mt-3">
                      <span className="flex items-center gap-1 text-xs text-text-muted">
                        <Users size={11} />
                        {event.article_count} source{event.article_count !== 1 ? 's' : ''}
                      </span>
                      {event.first_seen && (
                        <span className="flex items-center gap-1 text-xs text-text-muted">
                          <Clock size={11} />
                          {formatRelative(event.first_seen)}
                        </span>
                      )}
                      {event.confidence_score != null && (
                        <span className={cn('flex items-center gap-1 text-xs font-semibold', getTrustClass(event.confidence_score))}>
                          <Shield size={11} />
                          {formatScore(event.confidence_score)}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Arrow */}
                  <div className="shrink-0 text-text-muted group-hover:text-primary transition-colors">
                    <ArrowRight size={18} />
                  </div>
                </Link>
              </motion.article>
            ))}

            {!data?.items?.length && (
              <div className="text-center py-20 text-text-muted">
                <Zap size={36} className="mx-auto mb-3 opacity-20" />
                <p>No events yet. Events appear when multiple sources cover the same story.</p>
              </div>
            )}

            {/* Pagination */}
            {data && data.total > 15 && (
              <div className="flex items-center justify-center gap-3 mt-8">
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="btn-outline disabled:opacity-30">Previous</button>
                <span className="text-sm text-text-muted">Page {page} of {Math.ceil(data.total / 15)}</span>
                <button onClick={() => setPage(p => p + 1)} disabled={!data.has_next} className="btn-outline disabled:opacity-30">Next <ArrowRight size={14} /></button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

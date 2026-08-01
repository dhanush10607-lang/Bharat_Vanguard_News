'use client';
import { useQuery } from '@tanstack/react-query';
import { notFound, useParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { Clock, Shield, Users, ExternalLink, Globe, ArrowLeft, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { eventsApi } from '@/lib/api';
import { TrustScore } from '@/components/news/TrustScore';
import {
  formatRelative, formatDate, getCategoryBadgeClass, getTrustClass,
  formatScore, getCountryFlag, cn
} from '@/lib/utils';

export default function EventDetailPage() {
  const { slug } = useParams<{ slug: string }>();

  const { data: event, isLoading, isError } = useQuery({
    queryKey: ['event', slug],
    queryFn: () => eventsApi.get(slug),
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="skeleton h-8 w-48 rounded mb-6" />
          <div className="skeleton h-12 w-full rounded mb-4" />
          <div className="skeleton h-4 w-2/3 rounded" />
        </div>
      </div>
    );
  }

  if (isError || !event) return notFound();

  const primaryArticle = event.articles.find(a => a.is_primary) || event.articles[0];

  return (
    <div className="pt-20 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <Link href="/events" className="inline-flex items-center gap-2 text-sm text-text-muted hover:text-text-primary transition-colors mb-6">
          <ArrowLeft size={16} />
          All events
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* ── Main ── */}
          <div className="lg:col-span-2">
            {/* Badges */}
            <div className="flex flex-wrap items-center gap-3 mb-4">
              {event.category && (
                <span className={getCategoryBadgeClass(event.category)}>{event.category}</span>
              )}
              {event.country && (
                <span className="text-xs text-text-muted">{getCountryFlag(event.country)} {event.country}</span>
              )}
              <span className="flex items-center gap-1.5 text-xs text-text-muted">
                <Users size={12} />
                {event.article_count} sources covering this story
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold text-text-primary leading-tight mb-4">
              {event.title}
            </h1>

            {event.first_seen && (
              <div className="flex items-center gap-4 text-sm text-text-muted mb-6">
                <span className="flex items-center gap-1.5">
                  <Clock size={13} />
                  First reported {formatDate(event.first_seen)}
                </span>
                <span className="flex items-center gap-1.5">
                  Updated {formatRelative(event.last_updated)}
                </span>
              </div>
            )}

            {/* AI Summary */}
            {(event.summary_medium || event.summary_bullets?.length) && (
              <div className="mb-8 p-5 bg-primary/5 border border-primary/20 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-5 h-5 rounded-md bg-primary/20 flex items-center justify-center">
                    <span className="text-xs">✦</span>
                  </div>
                  <span className="text-xs font-semibold text-primary-light uppercase tracking-wide">
                    AI Summary — {event.article_count} sources combined
                  </span>
                </div>

                {event.summary_bullets?.length ? (
                  <ul className="space-y-2">
                    {event.summary_bullets.map((point: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                        <CheckCircle size={14} className="text-emerald mt-0.5 shrink-0" />
                        {point}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-text-secondary leading-relaxed">{event.summary_medium}</p>
                )}
              </div>
            )}

            {/* Articles from different publishers */}
            <div>
              <h2 className="text-base font-semibold text-text-primary mb-4 flex items-center gap-2">
                <Globe size={16} className="text-primary" />
                Coverage from {event.article_count} publisher{event.article_count !== 1 ? 's' : ''}
              </h2>

              <div className="space-y-3">
                {event.articles.map((article, i) => (
                  <motion.div
                    key={article.article_id}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.06 }}
                    className="card p-4 group"
                  >
                    <div className="flex items-start gap-3">
                      {/* Publisher logo */}
                      <div className="w-8 h-8 rounded-lg bg-surface-2 border border-border flex items-center justify-center shrink-0 overflow-hidden">
                        {article.publisher?.logo_url ? (
                          <Image src={article.publisher.logo_url} alt={article.publisher.name || ''} width={28} height={28} className="object-contain" />
                        ) : (
                          <Globe size={14} className="text-text-muted" />
                        )}
                      </div>

                      <div className="flex-1 min-w-0">
                        {article.is_primary && (
                          <span className="inline-flex items-center gap-1 text-2xs text-emerald font-semibold mb-1">
                            <CheckCircle size={10} /> Primary Source
                          </span>
                        )}

                        <Link href={`/news/${article.slug}`} className="block">
                          <h3 className="text-sm font-semibold text-text-primary group-hover:text-primary-light transition-colors line-clamp-2 mb-1">
                            {article.title}
                          </h3>
                        </Link>

                        <div className="flex flex-wrap items-center gap-3">
                          {article.publisher && (
                            <span className="text-xs font-medium text-primary-light">{article.publisher.name}</span>
                          )}
                          {article.publisher?.country && (
                            <span className="text-xs text-text-muted">{getCountryFlag(article.publisher.country)}</span>
                          )}
                          {article.published_time && (
                            <span className="text-xs text-text-muted flex items-center gap-1">
                              <Clock size={10} />
                              {formatRelative(article.published_time)}
                            </span>
                          )}
                          {article.confidence_score != null && (
                            <span className={cn('text-xs font-semibold flex items-center gap-1', getTrustClass(article.confidence_score))}>
                              <Shield size={10} />
                              {formatScore(article.confidence_score)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* ── Sidebar ── */}
          <aside className="space-y-4">
            {event.confidence_score != null && (
              <TrustScore
                data={{
                  confidence_score: event.confidence_score,
                  independent_sources: event.article_count || 0,
                  cross_confirmation: (event.article_count || 0) > 1,
                }}
              />
            )}

            {/* Keywords */}
            {event.keywords?.length > 0 && (
              <div className="card p-5">
                <h3 className="text-sm font-semibold text-text-primary mb-3">Related Topics</h3>
                <div className="flex flex-wrap gap-2">
                  {event.keywords.map((kw: string) => (
                    <Link
                      key={kw}
                      href={`/search?q=${encodeURIComponent(kw)}`}
                      className="px-2.5 py-1 rounded-lg text-xs bg-surface-2 text-text-muted hover:text-primary-light border border-border hover:border-primary/30 transition-colors"
                    >
                      #{kw}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Sentiment */}
            {event.sentiment && (
              <div className="card p-5">
                <h3 className="text-sm font-semibold text-text-primary mb-2">Coverage Tone</h3>
                <span className={cn(
                  'capitalize text-sm font-semibold',
                  event.sentiment === 'positive' ? 'text-emerald' :
                  event.sentiment === 'negative' ? 'text-rose' :
                  event.sentiment === 'mixed' ? 'text-amber' : 'text-text-muted'
                )}>
                  {event.sentiment}
                </span>
              </div>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}

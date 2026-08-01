import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { Clock, ExternalLink, User, Globe, ArrowLeft } from 'lucide-react';
import { articlesApi } from '@/lib/api';
import { TrustScore } from '@/components/news/TrustScore';
import { getCategoryBadgeClass, formatDate, formatRelative, getCountryFlag } from '@/lib/utils';

interface Props {
  params: { slug: string };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const article = await articlesApi.get(params.slug);
    return {
      title: article.title,
      description: article.description || article.summary_short,
      openGraph: {
        title: article.title,
        description: article.description || '',
        images: article.image_url ? [{ url: article.image_url }] : [],
        type: 'article',
      },
    };
  } catch {
    return { title: 'Article Not Found' };
  }
}

export default async function ArticlePage({ params }: Props) {
  let article;
  try {
    article = await articlesApi.get(params.slug);
  } catch {
    notFound();
  }

  const trustData = {
    confidence_score: article.confidence_score,
    official_source: article.publisher?.is_official,
    publisher_reputation: article.publisher?.reputation_score,
  };

  return (
    <div className="pt-20 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">

        {/* Back button */}
        <Link href="/" className="inline-flex items-center gap-2 text-sm text-text-muted hover:text-text-primary transition-colors mb-6">
          <ArrowLeft size={16} />
          Back to news
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* ── Main Content ── */}
          <article className="lg:col-span-2 max-w-3xl mx-auto w-full" itemScope itemType="https://schema.org/NewsArticle">

            {/* Category + meta */}
            <div className="flex flex-wrap items-center gap-3 mb-4">
              {article.category && (
                <span className={getCategoryBadgeClass(article.category)}>
                  {article.category}
                </span>
              )}
              {article.country && (
                <span className="text-xs text-text-muted">
                  {getCountryFlag(article.country)} {article.country}
                </span>
              )}
              {article.published_time && (
                <time
                  dateTime={article.published_time}
                  className="text-xs text-text-muted flex items-center gap-1"
                >
                  <Clock size={11} />
                  {formatDate(article.published_time)} · {formatRelative(article.published_time)}
                </time>
              )}
              {article.reading_time_min && (
                <span className="text-xs text-text-muted">{article.reading_time_min} min read</span>
              )}
            </div>

            {/* Title */}
            <h1
              className="text-3xl sm:text-4xl md:text-5xl font-bold leading-tight text-text-primary mb-6"
              itemProp="headline"
            >
              {article.title}
            </h1>

            {/* Description */}
            {article.description && (
              <p className="text-xl text-text-secondary leading-relaxed mb-8 border-l-4 border-primary pl-5">
                {article.description}
              </p>
            )}

            {/* Publisher info */}
            {article.publisher && (
              <div className="flex items-center gap-4 mb-8 p-5 bg-surface rounded-2xl border border-border">
                <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-surface-2 shrink-0">
                  {article.publisher.logo_url ? (
                    <Image
                      src={article.publisher.logo_url}
                      alt={article.publisher.name}
                      width={36}
                      height={36}
                      className="rounded object-contain"
                    />
                  ) : (
                    <Globe size={20} className="text-text-muted" />
                  )}
                </div>
                <div>
                  <p className="text-base font-semibold text-text-primary">{article.publisher.name}</p>
                  <p className="text-sm text-text-muted">
                    {getCountryFlag(article.publisher.country)} {article.publisher.country}
                    {article.publisher.is_official && (
                      <span className="ml-2 badge badge-science text-xs">Official</span>
                    )}
                  </p>
                </div>
                {article.author && (
                  <div className="ml-auto flex items-center gap-2 text-sm text-text-muted bg-surface-2 px-3 py-1.5 rounded-lg border border-border/50">
                    <User size={14} />
                    {article.author}
                  </div>
                )}
              </div>
            )}

            {/* Hero image */}
            {article.image_url && (
              <div className="relative w-full aspect-video rounded-3xl overflow-hidden mb-10 bg-surface-2 shadow-sm">
                <Image
                  src={article.image_url}
                  alt={article.title}
                  fill
                  sizes="(max-width: 1024px) 100vw, 66vw"
                  className="object-cover"
                  priority
                  unoptimized={true}
                />
              </div>
            )}

            {/* AI Summary (if available) */}
            {article.summary_medium && (
              <div className="mb-10 p-6 sm:p-8 bg-primary/5 border border-primary/20 rounded-3xl shadow-sm">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 rounded-xl bg-primary/20 flex items-center justify-center text-primary">
                    <span>✦</span>
                  </div>
                  <span className="text-sm font-bold text-primary-light uppercase tracking-widest">
                    AI Summary
                  </span>
                </div>

                {article.summary_bullets && article.summary_bullets.length > 0 ? (
                  <ul className="space-y-4">
                    {article.summary_bullets.map((point, i) => (
                      <li key={i} className="flex items-start gap-3 text-base sm:text-lg text-text-secondary leading-relaxed">
                        <span className="text-primary mt-1 text-xl">•</span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-base sm:text-lg text-text-secondary leading-relaxed">{article.summary_medium}</p>
                )}
              </div>
            )}

            {/* Full content */}
            <div className="article-body mb-12 text-lg sm:text-xl text-text-primary leading-loose space-y-6 font-serif">
              {article.content ? (
                article.content.split('\n\n').map((paragraph, i) => (
                  <p key={i}>{paragraph}</p>
                ))
              ) : (
                <>
                  <p>{article.description}</p>
                  <p className="text-text-muted text-base mt-6 italic">
                    Full article content is fetched after the parser processes this article.
                  </p>
                </>
              )}
            </div>

            {/* Keywords */}
            {article.keywords && article.keywords.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 mb-10 pt-6 border-t border-border">
                <span className="text-sm font-medium text-text-muted mr-2">Topics:</span>
                {article.keywords.map((kw) => (
                  <Link
                    key={kw}
                    href={`/search?q=${encodeURIComponent(kw)}`}
                    className="px-3 py-1.5 rounded-full text-sm bg-surface-2 text-text-secondary hover:text-primary-light hover:bg-primary/10 transition-colors border border-border/50"
                  >
                    #{kw}
                  </Link>
                ))}
              </div>
            )}

            {/* Read original */}
            {article.url && (
              <div className="pb-10">
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  id="btn-read-original"
                  className="btn-outline inline-flex items-center gap-2 py-3 px-6 rounded-xl hover:bg-surface-2 transition-colors"
                >
                  <ExternalLink size={18} />
                  <span className="font-medium">Read original article on {article.publisher?.name || 'source website'}</span>
                </a>
              </div>
            )}
          </article>

          {/* ── Sidebar ── */}
          <aside className="space-y-6 lg:pl-4">
            {/* Trust Score */}
            <TrustScore data={trustData} />

            {/* Article stats */}
            <div className="card p-6 bg-surface border border-border rounded-3xl">
              <h3 className="text-base font-bold text-text-primary mb-4 border-b border-border/50 pb-3">Article Info</h3>
              <dl className="space-y-4">
                {[
                  { label: 'Language',  value: article.language?.toUpperCase() || 'EN' },
                  { label: 'Words',     value: article.word_count?.toLocaleString() || '—' },
                  { label: 'Read time', value: `${article.reading_time_min || '—'} min` },
                  { label: 'Sentiment', value: article.sentiment || 'Not analyzed' },
                ].map(({ label, value }) => (
                  <div key={label} className="flex justify-between items-center text-sm">
                    <dt className="text-text-muted">{label}</dt>
                    <dd className="text-text-primary font-semibold capitalize bg-surface-2 px-2 py-1 rounded-md">{value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

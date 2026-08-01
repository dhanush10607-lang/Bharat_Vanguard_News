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
          <article className="lg:col-span-2" itemScope itemType="https://schema.org/NewsArticle">

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
              className="text-2xl sm:text-3xl md:text-4xl font-bold leading-tight text-text-primary mb-4"
              itemProp="headline"
            >
              {article.title}
            </h1>

            {/* Description */}
            {article.description && (
              <p className="text-lg text-text-secondary leading-relaxed mb-6 border-l-2 border-primary pl-4">
                {article.description}
              </p>
            )}

            {/* Publisher info */}
            {article.publisher && (
              <div className="flex items-center gap-3 mb-6 p-4 bg-surface rounded-xl border border-border">
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-surface-2">
                  {article.publisher.logo_url ? (
                    <Image
                      src={article.publisher.logo_url}
                      alt={article.publisher.name}
                      width={32}
                      height={32}
                      className="rounded object-contain"
                    />
                  ) : (
                    <Globe size={18} className="text-text-muted" />
                  )}
                </div>
                <div>
                  <p className="text-sm font-semibold text-text-primary">{article.publisher.name}</p>
                  <p className="text-xs text-text-muted">
                    {getCountryFlag(article.publisher.country)} {article.publisher.country}
                    {article.publisher.is_official && (
                      <span className="ml-2 badge badge-science text-2xs">Official</span>
                    )}
                  </p>
                </div>
                {article.author && (
                  <div className="ml-auto flex items-center gap-1.5 text-xs text-text-muted">
                    <User size={12} />
                    {article.author}
                  </div>
                )}
              </div>
            )}

            {/* Hero image */}
            {article.image_url && (
              <div className="relative w-full aspect-video rounded-2xl overflow-hidden mb-8 bg-surface-2">
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
              <div className="mb-8 p-5 bg-primary/5 border border-primary/20 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-5 h-5 rounded-md bg-primary/20 flex items-center justify-center">
                    <span className="text-xs">✦</span>
                  </div>
                  <span className="text-xs font-semibold text-primary-light uppercase tracking-wide">
                    AI Summary
                  </span>
                </div>

                {article.summary_bullets && article.summary_bullets.length > 0 ? (
                  <ul className="space-y-2">
                    {article.summary_bullets.map((point, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                        <span className="text-primary mt-0.5">•</span>
                        {point}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-text-secondary leading-relaxed">{article.summary_medium}</p>
                )}
              </div>
            )}

            {/* Full content */}
            {article.content ? (
              <div className="article-body mb-8">
                {article.content.split('\n\n').map((paragraph, i) => (
                  <p key={i}>{paragraph}</p>
                ))}
              </div>
            ) : (
              <div className="article-body mb-8">
                <p>{article.description}</p>
                <p className="text-text-muted text-sm mt-4">
                  Full article content is fetched after the parser processes this article.
                </p>
              </div>
            )}

            {/* Keywords */}
            {article.keywords && article.keywords.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-8">
                <span className="text-xs text-text-muted">Topics:</span>
                {article.keywords.map((kw) => (
                  <Link
                    key={kw}
                    href={`/search?q=${encodeURIComponent(kw)}`}
                    className="px-2.5 py-1 rounded-lg text-xs bg-surface-2 text-text-muted hover:text-primary-light hover:bg-primary/10 transition-colors border border-border"
                  >
                    #{kw}
                  </Link>
                ))}
              </div>
            )}

            {/* Read original */}
            {article.url && (
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                id="btn-read-original"
                className="btn-outline inline-flex"
              >
                <ExternalLink size={14} />
                Read original article
              </a>
            )}
          </article>

          {/* ── Sidebar ── */}
          <aside className="space-y-4">
            {/* Trust Score */}
            <TrustScore data={trustData} />

            {/* Article stats */}
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-text-primary mb-3">Article Info</h3>
              <dl className="space-y-2">
                {[
                  { label: 'Language',  value: article.language?.toUpperCase() || 'EN' },
                  { label: 'Words',     value: article.word_count?.toLocaleString() || '—' },
                  { label: 'Read time', value: `${article.reading_time_min || '—'} min` },
                  { label: 'Sentiment', value: article.sentiment || 'Not analyzed' },
                ].map(({ label, value }) => (
                  <div key={label} className="flex justify-between text-xs">
                    <dt className="text-text-muted">{label}</dt>
                    <dd className="text-text-primary font-medium capitalize">{value}</dd>
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

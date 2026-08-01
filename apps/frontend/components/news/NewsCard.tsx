'use client';
import Link from 'next/link';
import Image from 'next/image';
import { Clock, Shield, ExternalLink } from 'lucide-react';
import { motion } from 'framer-motion';
import type { Article } from '@/lib/api';
import {
  cn, formatRelative, getCategoryBadgeClass, getTrustClass,
  formatScore, getCountryFlag, truncate
} from '@/lib/utils';

// ============================================================
//  NEWS CARD — Standard card for grids and feeds
// ============================================================

interface NewsCardProps {
  article: Article;
  index?: number;
  showPublisher?: boolean;
  compact?: boolean;
}

export function NewsCard({ article, index = 0, showPublisher = true, compact = false }: NewsCardProps) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.05 }}
      className="card group cursor-pointer h-full flex flex-col"
    >
      <Link href={`/news/${article.slug}`} className="flex flex-col h-full">
        {/* Image */}
        {!compact && article.image_url && (
          <div className="relative w-full aspect-video overflow-hidden bg-surface-2">
            <Image
              src={article.image_url}
              alt={article.title}
              fill
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              className="object-cover transition-transform duration-500 group-hover:scale-105"
              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
            />
            {/* Category badge overlay */}
            {article.category && (
              <div className="absolute top-3 left-3">
                <span className={getCategoryBadgeClass(article.category)}>
                  {article.category}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Content */}
        <div className={cn('flex flex-col flex-1', compact ? 'p-4' : 'p-5')}>
          {/* Category (for compact cards without image) */}
          {(compact || !article.image_url) && article.category && (
            <span className={cn(getCategoryBadgeClass(article.category), 'mb-2 self-start')}>
              {article.category}
            </span>
          )}

          {/* Title */}
          <h3
            className={cn(
              'font-bold text-text-primary leading-snug mb-2 transition-colors group-hover:text-primary-light',
              compact ? 'text-sm line-clamp-2' : 'text-base line-clamp-3'
            )}
          >
            {article.title}
          </h3>

          {/* Description */}
          {!compact && article.description && (
            <p className="text-sm text-text-muted line-clamp-2 mb-3 leading-relaxed">
              {article.description}
            </p>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between mt-auto pt-3 border-t border-border/50">
            {/* Publisher + time */}
            <div className="flex items-center gap-2 min-w-0">
              {showPublisher && article.publisher && (
                <span className="text-xs font-medium text-primary-light truncate max-w-[100px]">
                  {article.publisher.name}
                </span>
              )}
              {article.published_time && (
                <>
                  {showPublisher && <span className="text-text-muted text-xs">·</span>}
                  <span className="text-xs text-text-muted flex items-center gap-1">
                    <Clock size={10} />
                    {formatRelative(article.published_time)}
                  </span>
                </>
              )}
            </div>

            {/* Trust score */}
            {article.confidence_score != null && (
              <div className="flex items-center gap-1 shrink-0">
                <Shield size={10} className={getTrustClass(article.confidence_score)} />
                <span className={cn('text-xs font-semibold', getTrustClass(article.confidence_score))}>
                  {formatScore(article.confidence_score)}
                </span>
              </div>
            )}
          </div>
        </div>
      </Link>
    </motion.article>
  );
}

// ============================================================
//  HERO CARD — Large featured article at top of home page
// ============================================================

export function HeroCard({ article }: { article: Article }) {
  return (
    <motion.article
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="relative rounded-3xl overflow-hidden group cursor-pointer"
      style={{ minHeight: '420px' }}
    >
      <Link href={`/news/${article.slug}`}>
        {/* Background image */}
        <div className="absolute inset-0 bg-surface-2">
          {article.image_url && (
            <Image
              src={article.image_url}
              alt={article.title}
              fill
              sizes="100vw"
              className="object-cover opacity-60 transition-all duration-700 group-hover:opacity-70 group-hover:scale-105"
              priority
            />
          )}
          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/70 to-transparent" />
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-end h-full p-6 md:p-8" style={{ minHeight: '420px' }}>
          <div className="flex items-center gap-3 mb-3">
            {article.category && (
              <span className={getCategoryBadgeClass(article.category)}>
                {article.category}
              </span>
            )}
            <span className="flex items-center gap-1">
              <span className="dot-live" />
              <span className="text-xs text-rose-400 font-medium">BREAKING</span>
            </span>
          </div>

          <h1 className="text-2xl md:text-4xl font-bold text-white leading-tight mb-3 max-w-2xl group-hover:text-primary-light transition-colors">
            {article.title}
          </h1>

          {article.description && (
            <p className="text-sm md:text-base text-gray-300 line-clamp-2 mb-4 max-w-xl">
              {article.description}
            </p>
          )}

          <div className="flex items-center gap-4 flex-wrap">
            {article.publisher && (
              <span className="text-sm font-semibold text-primary-light">
                {article.publisher.name}
              </span>
            )}
            {article.published_time && (
              <span className="text-sm text-gray-400 flex items-center gap-1">
                <Clock size={12} />
                {formatRelative(article.published_time)}
              </span>
            )}
            {article.reading_time_min && (
              <span className="text-sm text-gray-400">{article.reading_time_min} min read</span>
            )}
            {article.confidence_score != null && (
              <div className="flex items-center gap-1">
                <Shield size={12} className={getTrustClass(article.confidence_score)} />
                <span className={cn('text-sm font-semibold', getTrustClass(article.confidence_score))}>
                  {formatScore(article.confidence_score)} confidence
                </span>
              </div>
            )}
          </div>
        </div>
      </Link>
    </motion.article>
  );
}

// ============================================================
//  SKELETON LOADER — for loading states
// ============================================================

export function NewsCardSkeleton({ compact = false }: { compact?: boolean }) {
  return (
    <div className="card overflow-hidden">
      {!compact && <div className="skeleton aspect-video" />}
      <div className={compact ? 'p-4' : 'p-5'} >
        <div className="skeleton h-4 w-16 rounded mb-3" />
        <div className="skeleton h-5 w-full rounded mb-2" />
        <div className="skeleton h-5 w-3/4 rounded mb-3" />
        {!compact && <div className="skeleton h-4 w-full rounded mb-1" />}
        {!compact && <div className="skeleton h-4 w-2/3 rounded mb-4" />}
        <div className="flex justify-between mt-3 pt-3 border-t border-border/50">
          <div className="skeleton h-3 w-24 rounded" />
          <div className="skeleton h-3 w-12 rounded" />
        </div>
      </div>
    </div>
  );
}

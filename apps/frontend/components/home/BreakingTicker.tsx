import Link from 'next/link';
import { articlesApi } from '@/lib/api';
import { Clock } from 'lucide-react';

export async function BreakingTicker() {
  let articles = [];
  try {
    // Fetch top 5 breaking news
    articles = await articlesApi.breaking(5);
  } catch (error) {
    return null;
  }

  if (!articles || articles.length === 0) return null;

  return (
    <div className="w-full bg-red-600 text-white overflow-hidden flex items-center h-10 px-2 sm:px-4">
      <div className="flex items-center gap-1.5 sm:gap-2 font-bold uppercase text-[10px] sm:text-xs shrink-0 tracking-widest z-10 bg-red-600 pr-2 sm:pr-4">
        <span className="dot-live bg-white" />
        <span className="hidden sm:inline">Breaking News</span>
        <span className="sm:hidden">Breaking</span>
      </div>
      
      {/* CSS Marquee */}
      <div className="flex flex-1 overflow-hidden relative">
        <div className="animate-marquee whitespace-nowrap flex items-center gap-8 pl-4">
          {articles.map((article) => (
            <Link 
              key={article.article_id} 
              href={`/news/${article.slug}`}
              className="flex items-center gap-3 hover:underline text-sm font-medium transition-all"
            >
              <Clock size={12} className="opacity-70" />
              {article.title}
            </Link>
          ))}
          {/* Duplicate for seamless loop */}
          {articles.map((article) => (
            <Link 
              key={article.article_id + '_dup'} 
              href={`/news/${article.slug}`}
              className="flex items-center gap-3 hover:underline text-sm font-medium transition-all"
            >
              <Clock size={12} className="opacity-70" />
              {article.title}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

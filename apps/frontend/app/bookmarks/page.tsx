'use client';

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { Bookmark, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { authApi } from '@/lib/api';
import { NewsCard, NewsCardSkeleton } from '@/components/news/NewsCard';
import { getStoredUser } from '@/lib/utils';
import { motion } from 'framer-motion';

export default function BookmarksPage() {
  const router = useRouter();
  const [isMounted, setIsMounted] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    setIsMounted(true);
    const currentUser = getStoredUser();
    setUser(currentUser);
    if (!currentUser) {
      router.push('/login');
    }
  }, [router]);

  const { data, isLoading } = useQuery({
    queryKey: ['bookmarks-details'],
    queryFn: authApi.getBookmarkDetails,
    enabled: !!user,
  });

  if (!isMounted || !user) return null;

  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        
        {/* Header */}
        <div className="mb-10">
          <Link href="/" className="inline-flex items-center gap-2 text-sm text-text-muted hover:text-text-primary transition-colors mb-6">
            <ArrowLeft size={16} /> Back to Home
          </Link>
          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald/10 text-emerald rounded-xl">
              <Bookmark size={24} className="fill-current" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-text-primary mb-1">Your Bookmarks</h1>
              <p className="text-text-muted">Saved articles to read later</p>
            </div>
          </div>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <NewsCardSkeleton key={i} />
            ))}
          </div>
        ) : !data?.items || data.items.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-20 bg-surface rounded-3xl border border-border/50 text-center"
          >
            <Bookmark size={48} className="text-text-muted/30 mb-4" />
            <h3 className="text-xl font-semibold text-text-primary mb-2">No bookmarks yet</h3>
            <p className="text-text-muted max-w-sm mb-6">
              When you find an article you want to read later, click the bookmark icon to save it here.
            </p>
            <Link href="/" className="btn-primary">
              Discover News
            </Link>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.items.map((article, idx) => (
              <NewsCard key={article.article_id} article={article} index={idx} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

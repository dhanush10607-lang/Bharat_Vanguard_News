'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';
import { articlesApi, type Article } from '@/lib/api';
import { NewsCard, NewsCardSkeleton } from '@/components/news/NewsCard';
import { Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

export default function FeedPage() {
  const router = useRouter();
  const supabase = createClient();
  
  const [loading, setLoading] = useState(true);
  const [articles, setArticles] = useState<Article[]>([]);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const fetchUserAndFeed = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error || !session) {
          router.push('/login');
          return;
        }
        
        setUser(session.user);

        // Ideally, we'd fetch user preferences (like categories) from the DB
        // For now, let's fetch 'technology' and 'science' as an example for the personalized feed
        const res = await articlesApi.list({ page: 1, page_size: 12 }); // Fetch general list for now if no specific preference API is ready
        
        if (res && res.items) {
          setArticles(res.items);
        }
      } catch (err) {
        console.error(err);
        toast.error('Failed to load personalized feed');
      } finally {
        setLoading(false);
      }
    };

    fetchUserAndFeed();
  }, [router, supabase.auth]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl pt-24">
        <h1 className="text-3xl font-bold text-text-primary mb-8">My Feed</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <NewsCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl pt-24">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-primary/20 border border-primary/30 flex items-center justify-center">
          <Zap size={20} className="text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-text-primary">My Feed</h1>
          <p className="text-text-muted text-sm mt-1">Personalized news based on your preferences</p>
        </div>
      </div>

      {articles.length === 0 ? (
        <div className="text-center py-20 bg-surface border border-border rounded-xl">
          <p className="text-text-muted">No articles found for your feed yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {articles.map((article, idx) => (
            <NewsCard key={article.article_id} article={article} index={idx} />
          ))}
        </div>
      )}
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { Heart } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi } from '@/lib/api';
import { getStoredUser } from '@/lib/utils';
import { useRouter } from 'next/navigation';

interface LikeButtonProps {
  articleId: string;
  initialLikes?: number;
  className?: string;
  size?: number;
  showCount?: boolean;
}

export function LikeButton({ articleId, initialLikes = 0, className = '', size = 18, showCount = false }: LikeButtonProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [user, setUser] = useState<any>(null);
  const [localLikesCount, setLocalLikesCount] = useState(initialLikes);

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  // Only fetch likes if user is logged in
  const { data: likesData } = useQuery({
    queryKey: ['likes'],
    queryFn: authApi.getLikes,
    enabled: !!user,
    staleTime: 5 * 60 * 1000,
  });

  const isLiked = likesData?.liked_article_ids?.includes(articleId) || false;

  const toggleMutation = useMutation({
    mutationFn: () => authApi.toggleLike(articleId),
    onMutate: async () => {
      if (!user) {
        toast('Please log in to like articles', {
          action: {
            label: 'Login',
            onClick: () => router.push('/login'),
          },
        });
        throw new Error('Not logged in');
      }

      await queryClient.cancelQueries({ queryKey: ['likes'] });
      const previousLikes = queryClient.getQueryData(['likes']);

      queryClient.setQueryData(['likes'], (old: any) => {
        if (!old) return { liked_article_ids: [articleId] };
        const ids = old.liked_article_ids || [];
        const newIds = ids.includes(articleId)
          ? ids.filter((id: string) => id !== articleId)
          : [...ids, articleId];
        return { ...old, liked_article_ids: newIds };
      });

      // Optimistically update local count
      setLocalLikesCount(prev => isLiked ? Math.max(0, prev - 1) : prev + 1);

      return { previousLikes };
    },
    onError: (err, newTodo, context: any) => {
      if (err.message !== 'Not logged in' && context?.previousLikes) {
        queryClient.setQueryData(['likes'], context.previousLikes);
        setLocalLikesCount(initialLikes); // revert local state
        toast.error('Failed to like article');
      }
    },
    onSettled: (data, err) => {
      if (!err || err.message !== 'Not logged in') {
        queryClient.invalidateQueries({ queryKey: ['likes'] });
      }
    },
  });

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    toggleMutation.mutate();
  };

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={handleClick}
      className={`relative p-2 rounded-full flex items-center justify-center gap-1.5 transition-all ${
        isLiked 
          ? 'bg-rose-500/10 text-rose-500 hover:bg-rose-500/20' 
          : 'bg-surface-2 text-text-muted hover:text-rose-500 hover:bg-rose-500/10'
      } ${className}`}
      title={isLiked ? "Unlike article" : "Like article"}
    >
      <Heart 
        size={size} 
        className={isLiked ? "fill-current text-rose-500" : ""} 
      />
      {showCount && localLikesCount > 0 && (
        <span className="text-xs font-semibold">{localLikesCount}</span>
      )}
    </motion.button>
  );
}

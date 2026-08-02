'use client';

import { useState, useEffect } from 'react';
import { Bookmark } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi } from '@/lib/api';
import { getStoredUser } from '@/lib/utils';
import { useRouter } from 'next/navigation';

interface BookmarkButtonProps {
  articleId: string;
  className?: string;
  size?: number;
}

export function BookmarkButton({ articleId, className = '', size = 18 }: BookmarkButtonProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  // Only fetch bookmarks if user is logged in
  const { data: bookmarksData } = useQuery({
    queryKey: ['bookmarks'],
    queryFn: authApi.getBookmarks,
    enabled: !!user,
    staleTime: 5 * 60 * 1000,
  });

  const isBookmarked = bookmarksData?.bookmarked_article_ids?.includes(articleId) || false;

  const toggleMutation = useMutation({
    mutationFn: () => authApi.toggleBookmark(articleId),
    onMutate: async () => {
      if (!user) {
        toast('Please log in to save articles', {
          action: {
            label: 'Login',
            onClick: () => router.push('/login'),
          },
        });
        throw new Error('Not logged in');
      }

      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['bookmarks'] });

      // Snapshot the previous value
      const previousBookmarks = queryClient.getQueryData(['bookmarks']);

      // Optimistically update to the new value
      queryClient.setQueryData(['bookmarks'], (old: any) => {
        if (!old) return { bookmarked_article_ids: [articleId] };
        const ids = old.bookmarked_article_ids || [];
        const newIds = ids.includes(articleId)
          ? ids.filter((id: string) => id !== articleId)
          : [...ids, articleId];
        return { ...old, bookmarked_article_ids: newIds };
      });

      return { previousBookmarks };
    },
    onError: (err, newTodo, context: any) => {
      // Revert if error (unless it was just the login prompt)
      if (err.message !== 'Not logged in' && context?.previousBookmarks) {
        queryClient.setQueryData(['bookmarks'], context.previousBookmarks);
        toast.error('Failed to update bookmark');
      }
    },
    onSettled: (data, err) => {
      if (!err || err.message !== 'Not logged in') {
        queryClient.invalidateQueries({ queryKey: ['bookmarks'] });
        
        if (data?.status === 'added') {
          toast.success('Article saved to bookmarks');
        } else if (data?.status === 'removed') {
          toast.success('Removed from bookmarks');
        }
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
      className={`relative p-2 rounded-full flex items-center justify-center transition-all ${
        isBookmarked 
          ? 'bg-emerald/10 text-emerald hover:bg-emerald/20' 
          : 'bg-surface-2 text-text-muted hover:text-text-primary hover:bg-surface-3'
      } ${className}`}
      title={isBookmarked ? "Remove bookmark" : "Save article"}
    >
      <Bookmark 
        size={size} 
        className={isBookmarked ? "fill-current" : ""} 
      />
    </motion.button>
  );
}

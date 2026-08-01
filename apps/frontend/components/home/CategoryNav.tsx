'use client';
import Link from 'next/link';
import { motion } from 'framer-motion';

const CATEGORIES = [
  { href: '/categories/world',       label: 'World',       emoji: '🌍', color: 'from-purple-500/20 to-purple-600/5', border: 'border-purple-500/20 hover:border-purple-500/50' },
  { href: '/categories/technology',  label: 'Technology',  emoji: '💻', color: 'from-blue-500/20 to-blue-600/5',   border: 'border-blue-500/20 hover:border-blue-500/50' },
  { href: '/categories/ai',          label: 'AI',          emoji: '🤖', color: 'from-violet-500/20 to-violet-600/5', border: 'border-violet-500/20 hover:border-violet-500/50' },
  { href: '/categories/business',    label: 'Business',    emoji: '📈', color: 'from-amber-500/20 to-amber-600/5', border: 'border-amber-500/20 hover:border-amber-500/50' },
  { href: '/categories/science',     label: 'Science',     emoji: '🔬', color: 'from-emerald-500/20 to-emerald-600/5', border: 'border-emerald-500/20 hover:border-emerald-500/50' },
  { href: '/categories/health',      label: 'Health',      emoji: '🏥', color: 'from-rose-500/20 to-rose-600/5',  border: 'border-rose-500/20 hover:border-rose-500/50' },
  { href: '/categories/india',       label: 'India',       emoji: '🇮🇳', color: 'from-orange-500/20 to-orange-600/5', border: 'border-orange-500/20 hover:border-orange-500/50' },
  { href: '/categories/sports',      label: 'Sports',      emoji: '⚽', color: 'from-sky-500/20 to-sky-600/5',   border: 'border-sky-500/20 hover:border-sky-500/50' },
];

export function CategoryNav() {
  return (
    <div>
      <p className="text-xs text-text-muted mb-3 uppercase tracking-widest font-semibold">Browse by category</p>
      <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
        {CATEGORIES.map((cat, i) => (
          <motion.div
            key={cat.href}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
          >
            <Link
              href={cat.href}
              id={`category-${cat.label.toLowerCase()}`}
              className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border bg-gradient-to-b ${cat.color} ${cat.border} transition-all duration-200 hover:-translate-y-0.5 group`}
            >
              <span className="text-xl">{cat.emoji}</span>
              <span className="text-2xs font-medium text-text-muted group-hover:text-text-primary transition-colors text-center leading-tight">
                {cat.label}
              </span>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

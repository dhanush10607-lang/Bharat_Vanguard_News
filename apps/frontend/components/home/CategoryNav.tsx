'use client';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Globe, Laptop, Bot, TrendingUp, FlaskConical, Stethoscope, MapPin, Trophy } from 'lucide-react';

const CATEGORIES = [
  { href: '/categories/world',       label: 'World',       icon: Globe, color: 'from-purple-500/20 to-purple-600/5', border: 'border-purple-500/20 hover:border-purple-500/50', iconColor: 'text-purple-500' },
  { href: '/categories/technology',  label: 'Tech',        icon: Laptop, color: 'from-blue-500/20 to-blue-600/5',   border: 'border-blue-500/20 hover:border-blue-500/50', iconColor: 'text-blue-500' },
  { href: '/categories/ai',          label: 'AI',          icon: Bot, color: 'from-violet-500/20 to-violet-600/5', border: 'border-violet-500/20 hover:border-violet-500/50', iconColor: 'text-violet-500' },
  { href: '/categories/business',    label: 'Business',    icon: TrendingUp, color: 'from-amber-500/20 to-amber-600/5', border: 'border-amber-500/20 hover:border-amber-500/50', iconColor: 'text-amber-500' },
  { href: '/categories/science',     label: 'Science',     icon: FlaskConical, color: 'from-emerald-500/20 to-emerald-600/5', border: 'border-emerald-500/20 hover:border-emerald-500/50', iconColor: 'text-emerald-500' },
  { href: '/categories/health',      label: 'Health',      icon: Stethoscope, color: 'from-rose-500/20 to-rose-600/5',  border: 'border-rose-500/20 hover:border-rose-500/50', iconColor: 'text-rose-500' },
  { href: '/categories/india',       label: 'India',       icon: MapPin, color: 'from-orange-500/20 to-orange-600/5', border: 'border-orange-500/20 hover:border-orange-500/50', iconColor: 'text-orange-500' },
  { href: '/categories/sports',      label: 'Sports',      icon: Trophy, color: 'from-sky-500/20 to-sky-600/5',   border: 'border-sky-500/20 hover:border-sky-500/50', iconColor: 'text-sky-500' },
];

export function CategoryNav() {
  return (
    <div className="w-full">
      <p className="text-xs text-text-muted mb-3 uppercase tracking-widest font-semibold">Browse by category</p>
      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2">
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
              className={`flex flex-col items-center gap-2 p-3 sm:p-4 rounded-xl border bg-gradient-to-b ${cat.color} ${cat.border} transition-all duration-200 hover:-translate-y-0.5 group h-full`}
            >
              <cat.icon size={24} className={`${cat.iconColor} transition-transform group-hover:scale-110`} strokeWidth={1.5} />
              <span className="text-xs sm:text-2xs font-medium text-text-muted group-hover:text-text-primary transition-colors text-center leading-tight">
                {cat.label}
              </span>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

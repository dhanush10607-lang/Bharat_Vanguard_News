/**
 * Bharat Vanguard News (BVN) — Utility Functions
 */
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { formatDistanceToNow, format, parseISO } from 'date-fns';

/** Merge Tailwind classes safely */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** 
 * Safely parse ISO string, assuming UTC if no timezone is provided. 
 * This ensures backend naive datetimes are correctly converted to the user's local timezone.
 */
function safeParseISO(dateStr: string): Date {
  if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.match(/-\d{2}:\d{2}$/)) {
    return parseISO(`${dateStr}Z`);
  }
  return parseISO(dateStr);
}

/** Format a date string as relative ("2 hours ago") */
export function formatRelative(dateStr?: string | null): string {
  if (!dateStr) return 'Unknown date';
  try {
    return formatDistanceToNow(safeParseISO(dateStr), { addSuffix: true });
  } catch {
    return dateStr;
  }
}

export function stripHtml(html: string | null | undefined): string {
  if (!html) return '';
  return html.replace(/<[^>]*>?/gm, '').trim();
}

/** Format a date string as "Jul 31, 2026" */
export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '';
  try {
    return format(safeParseISO(dateStr), 'MMM d, yyyy');
  } catch {
    return dateStr;
  }
}

/** Format a date string as "Jul 31, 2026 at 9:00 PM" */
export function formatDateTime(dateStr?: string | null): string {
  if (!dateStr) return '';
  try {
    return format(safeParseISO(dateStr), "MMM d, yyyy 'at' h:mm a");
  } catch {
    return dateStr;
  }
}

/** Capitalize first letter of a string */
export function capitalize(str: string): string {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/** Truncate a string to max characters */
export function truncate(str: string, max: number): string {
  if (!str || str.length <= max) return str;
  return str.slice(0, max).trim() + '…';
}

/** Get CSS class for trust/confidence score */
export function getTrustClass(score?: number | null): string {
  if (score == null) return 'text-text-muted';
  if (score >= 0.7)  return 'text-emerald';
  if (score >= 0.4)  return 'text-amber';
  return 'text-rose';
}

/** Format number to compact notation (1.2K, 1.5M, etc) */
export function formatCompactNumber(number: number | undefined | null): string {
  if (number == null) return '0';
  return Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(number);
}

/** Get label for trust score */
export function getTrustLabel(score?: number | null): string {
  if (score == null) return 'Unverified';
  if (score >= 0.8)  return 'High Confidence';
  if (score >= 0.6)  return 'Moderate Confidence';
  if (score >= 0.4)  return 'Limited Sources';
  return 'Early Report';
}

/** Get CSS class for sentiment */
export function getSentimentClass(sentiment?: string | null): string {
  switch (sentiment) {
    case 'positive': return 'text-emerald';
    case 'negative': return 'text-rose';
    case 'neutral':  return 'text-text-muted';
    case 'mixed':    return 'text-amber';
    default:         return 'text-text-muted';
  }
}

/** Get badge class for a news category */
export function getCategoryBadgeClass(category?: string | null): string {
  const map: Record<string, string> = {
    technology:    'badge-tech',
    ai:            'badge-ai',
    world:         'badge-world',
    business:      'badge-business',
    finance:       'badge-business',
    science:       'badge-science',
    health:        'badge-health',
    india:         'badge-india',
    sports:        'badge-sports',
    entertainment: 'badge-default',
    politics:      'badge-world',
  };
  return map[category?.toLowerCase() || ''] || 'badge-default';
}

/** Format a confidence score as a percentage string */
export function formatScore(score?: number | null): string {
  if (score == null) return '—';
  return `${Math.round(score * 100)}%`;
}

/** Get flag emoji for a country name */
export function getCountryFlag(country?: string | null): string {
  const flags: Record<string, string> = {
    'India':         '🇮🇳',
    'United States': '🇺🇸',
    'United Kingdom':'🇬🇧',
    'UK':            '🇬🇧',
    'US':            '🇺🇸',
    'China':         '🇨🇳',
    'Russia':        '🇷🇺',
    'Germany':       '🇩🇪',
    'France':        '🇫🇷',
    'Japan':         '🇯🇵',
    'Australia':     '🇦🇺',
    'Canada':        '🇨🇦',
    'Brazil':        '🇧🇷',
    'Qatar':         '🇶🇦',
    'Global':        '🌍',
  };
  return flags[country || ''] || '🌐';
}

/** Save auth token and user to localStorage */
export function saveAuth(token: string, user: object): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('bvn_token', token);
  localStorage.setItem('bvn_user', JSON.stringify(user));
}

/** Clear auth from localStorage */
export function clearAuth(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('bvn_token');
  localStorage.removeItem('bvn_user');
}

/** Get stored user from localStorage */
export function getStoredUser(): any | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem('bvn_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

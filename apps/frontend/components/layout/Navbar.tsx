'use client';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Search, Menu, X, Zap, User, LogOut, Bookmark, ChevronDown } from 'lucide-react';
import { cn, getStoredUser, clearAuth } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

const NAV_LINKS = [
  { href: '/',              label: 'Home' },
  { href: '/search',        label: 'Search' },
  { href: '/analytics',     label: 'Analytics' },
  { href: '/magazine',      label: 'Magazine', badge: 'New' },
  {
    label: 'Categories',
    children: [
      { href: '/categories/world',         label: '🌍 World' },
      { href: '/categories/technology',    label: '💻 Technology' },
      { href: '/categories/ai',            label: '🤖 AI' },
      { href: '/categories/business',      label: '📈 Business' },
      { href: '/categories/science',       label: '🔬 Science' },
      { href: '/categories/health',        label: '🏥 Health' },
      { href: '/categories/india',         label: '🇮🇳 India' },
      { href: '/categories/sports',        label: '⚽ Sports' },
    ],
  },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    setUser(getStoredUser());
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    clearAuth();
    setUser(null);
    setUserMenuOpen(false);
    router.push('/');
  };

  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        scrolled ? 'navbar-blur' : 'bg-transparent'
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">

          {/* ── Logo ── */}
          <Link href="/" className="flex items-center gap-2 group" id="nav-logo">
            <img src="/BVNlogo.svg" alt="Bharat Vanguard News" className="h-8 sm:h-10 md:h-11 lg:h-12 w-auto transition-all" />
          </Link>

          {/* ── Desktop Nav ── */}
          <nav className="hidden md:flex items-center gap-1" aria-label="Main navigation">
            {NAV_LINKS.map((link) =>
              link.children ? (
                <div key={link.label} className="relative">
                  <button
                    id="nav-categories-btn"
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className={cn(
                      'flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-all',
                      dropdownOpen
                        ? 'text-text-primary bg-surface-2'
                        : 'text-text-secondary hover:text-text-primary hover:bg-surface-2'
                    )}
                  >
                    {link.label}
                    <ChevronDown size={14} className={cn('transition-transform', dropdownOpen && 'rotate-180')} />
                  </button>

                  <AnimatePresence>
                    {dropdownOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: -8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        transition={{ duration: 0.15 }}
                        className="absolute top-full left-0 mt-2 w-48 card-glass p-1.5 grid grid-cols-1 gap-0.5"
                        onMouseLeave={() => setDropdownOpen(false)}
                      >
                        {link.children.map((child) => (
                          <Link
                            key={child.href}
                            href={child.href}
                            onClick={() => setDropdownOpen(false)}
                            className="px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-surface-2 transition-colors"
                          >
                            {child.label}
                          </Link>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                <Link
                  key={link.href}
                  href={link.href!}
                  id={`nav-${link.label.toLowerCase()}`}
                  className={cn(
                    'px-3 py-2 rounded-lg text-sm font-medium transition-all',
                    pathname === link.href
                      ? 'text-text-primary bg-surface-2'
                      : 'text-text-secondary hover:text-text-primary hover:bg-surface-2'
                  )}
                >
                  {link.label}
                </Link>
              )
            )}
          </nav>

          {/* ── Right Side ── */}
          <div className="flex items-center gap-2">
            {/* Search icon */}
            <Link
              href="/search"
              id="nav-search-btn"
              className="p-2 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-2 transition-all"
              aria-label="Search"
            >
              <Search size={18} />
            </Link>

            {/* User menu or Login */}
            {user ? (
              <div className="relative">
                <button
                  id="nav-user-btn"
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-surface border border-border hover:border-border-2 transition-all"
                >
                  {user.avatar_url ? (
                    <img src={user.avatar_url} alt={user.display_name} className="w-6 h-6 rounded-full object-cover" />
                  ) : (
                    <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center">
                      <User size={12} className="text-primary" />
                    </div>
                  )}
                  <span className="text-sm font-medium text-text-primary hidden sm:block">
                    {user.display_name?.split(' ')[0] || user.username}
                  </span>
                  <ChevronDown size={12} className="text-text-muted" />
                </button>

                <AnimatePresence>
                  {userMenuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      transition={{ duration: 0.15 }}
                      className="absolute top-full right-0 mt-2 w-48 card-glass p-1.5"
                    >
                      <div className="px-3 py-2 border-b border-border mb-1">
                        <p className="text-sm font-medium text-text-primary">{user.display_name}</p>
                        <p className="text-2xs text-text-muted">{user.email}</p>
                      </div>
                      <Link
                        href="/bookmarks"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-2 w-full px-4 py-2 text-sm text-text-secondary hover:bg-surface-3 transition-colors"
                      >
                        <Bookmark size={14} /> Bookmarks
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-rose-400 hover:bg-rose/10 transition-colors"
                      >
                        <LogOut size={14} /> Sign out
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <Link
                href="/login"
                id="nav-login-btn"
                className="btn-primary text-xs py-1.5"
              >
                Sign in
              </Link>
            )}

            {/* Mobile menu button */}
            <button
              id="nav-mobile-menu-btn"
              className="md:hidden p-2 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-2 transition-all"
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label="Toggle menu"
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </div>

      {/* ── Mobile Menu ── */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-border bg-surface/95 backdrop-blur-xl"
          >
            <nav className="max-w-7xl mx-auto px-4 py-3 flex flex-col gap-1">
              {NAV_LINKS.map((link) =>
                link.children ? (
                  link.children.map((child) => (
                    <Link
                      key={child.href}
                      href={child.href}
                      onClick={() => setMobileOpen(false)}
                      className="px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-surface-2 transition-colors"
                    >
                      {child.label}
                    </Link>
                  ))
                ) : (
                  <Link
                    key={link.href}
                    href={link.href!}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      pathname === link.href ? 'text-text-primary bg-surface-2' : 'text-text-secondary hover:text-text-primary'
                    )}
                  >
                    {link.label}
                  </Link>
                )
              )}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

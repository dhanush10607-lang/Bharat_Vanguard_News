import Link from 'next/link';
import { Zap, Github, Twitter, Globe } from 'lucide-react';

const FOOTER_LINKS = {
  Platform: [
    { href: '/',           label: 'Home' },
    { href: '/search',     label: 'Search' },
    { href: '/analytics',  label: 'Analytics' },
    { href: '/events',     label: 'Events' },
  ],
  Categories: [
    { href: '/categories/world',       label: 'World' },
    { href: '/categories/technology',  label: 'Technology' },
    { href: '/categories/ai',          label: 'AI' },
    { href: '/categories/business',    label: 'Business' },
    { href: '/categories/science',     label: 'Science' },
    { href: '/categories/india',       label: 'India' },
  ],
  Company: [
    { href: '/about',      label: 'About' },
    { href: '/api',        label: 'Public API' },
    { href: '/publishers', label: 'Publishers' },
  ],
};

export function Footer() {
  return (
    <footer className="border-t border-border mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12">

        {/* ── Top Row ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-12">

          {/* Brand */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4 w-fit group">
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/20 border border-primary/30">
                <Zap size={16} className="text-primary" />
              </div>
              <span className="font-bold text-lg">
                <span className="text-gradient-blue">BVN</span>
                <span className="text-text-muted font-normal"> Bharat Vanguard</span>
              </span>
            </Link>
            <p className="text-sm text-text-muted max-w-xs leading-relaxed mb-4">
              AI-powered news intelligence platform. Transparent, searchable, and sourced.
            </p>
            <p className="text-xs text-text-muted leading-relaxed">
              <span className="text-amber font-medium">⚠ Note:</span> Trust scores indicate evidence
              strength, not proof of truth or falsehood. Always read primary sources.
            </p>
          </div>

          {/* Link groups */}
          {Object.entries(FOOTER_LINKS).map(([group, links]) => (
            <div key={group}>
              <h4 className="text-xs font-semibold uppercase tracking-widest text-text-muted mb-3">
                {group}
              </h4>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-sm text-text-muted hover:text-text-primary transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* ── Bottom Row ── */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-8 border-t border-border">
          <p className="text-xs text-text-muted">
            © {new Date().getFullYear()} Bharat Vanguard News (BVN). Built with transparency.
          </p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 text-xs text-text-muted">
              <span className="dot-online" />
              System operational
            </span>
            <div className="flex items-center gap-3">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-text-muted hover:text-text-primary transition-colors"
                aria-label="GitHub"
              >
                <Github size={16} />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-text-muted hover:text-text-primary transition-colors"
                aria-label="Twitter"
              >
                <Twitter size={16} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

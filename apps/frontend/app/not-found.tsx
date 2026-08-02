import Link from 'next/link';
import { Home, Search, AlertCircle } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center px-4 text-center">
      <div className="w-20 h-20 bg-surface-2 rounded-2xl flex items-center justify-center mb-6 border border-border shadow-2xl relative overflow-hidden group">
        <div className="absolute inset-0 bg-primary/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        <AlertCircle size={32} className="text-primary relative z-10" />
      </div>

      <h1 className="text-4xl md:text-5xl font-serif font-bold text-text-primary mb-3">
        Page Not Found
      </h1>
      
      <p className="text-text-secondary max-w-md mx-auto mb-8 text-lg">
        We couldn't find the page you're looking for. It might have been moved, deleted, or never existed in the first place.
      </p>

      <div className="flex flex-col sm:flex-row items-center gap-4">
        <Link 
          href="/" 
          className="btn-primary w-full sm:w-auto inline-flex items-center justify-center gap-2"
        >
          <Home size={18} />
          Back to Homepage
        </Link>
        <Link 
          href="/search" 
          className="btn-secondary w-full sm:w-auto inline-flex items-center justify-center gap-2"
        >
          <Search size={18} />
          Search News
        </Link>
      </div>
    </div>
  );
}

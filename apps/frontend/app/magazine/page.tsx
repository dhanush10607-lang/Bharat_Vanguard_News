import type { Metadata } from 'next';
import { BookOpen, Download } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Magazine — Bharat Vanguard News (BVN)',
  description: 'Download the AI-generated monthly magazine of the most important stories.',
};

// Temporarily hardcoded for display until backend starts generating
const MOCK_MAGAZINES = [
  {
    magazine_id: "1",
    title: "August 2026 Edition",
    month: 8,
    year: 2026,
    summary: "Our AI has compiled the most critical events and verified news stories from this month. Explore the geopolitical shifts and tech advancements that shaped the world.",
    pdf_url: "#",
    cover_image_url: null
  }
];

import { magazinesApi } from '@/lib/api';

export default async function MagazinePage() {
  let magazines = [];
  try {
    const res = await magazinesApi.list();
    if (res && res.items && res.items.length > 0) {
      magazines = res.items;
    } else {
      magazines = MOCK_MAGAZINES; // Fallback if no real magazines generated yet
    }
  } catch (err) {
    console.error("Failed to fetch magazines:", err);
    magazines = MOCK_MAGAZINES;
  } 

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-16 pb-24">
      <div className="text-center mb-16">
        <h1 className="text-4xl sm:text-5xl font-bold text-text-primary mb-6 flex items-center justify-center gap-4">
          <BookOpen className="text-primary" size={40} /> BVN Magazine
        </h1>
        <p className="text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed">
          At the end of every month, our AI engine compiles the most critical stories, verified events, and geopolitical shifts into a comprehensive digital book.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {magazines.map((mag) => (
          <div key={mag.magazine_id} className="card p-6 flex flex-col items-center text-center">
            <div className="w-48 h-64 bg-surface-2 border border-border rounded-lg shadow-lg flex items-center justify-center mb-6 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-b from-primary/20 to-transparent pointer-events-none" />
              <BookOpen size={48} className="text-text-muted opacity-50" />
            </div>
            
            <h2 className="text-2xl font-bold text-text-primary mb-2">{mag.title}</h2>
            <p className="text-sm text-text-secondary mb-6 leading-relaxed flex-1">
              {mag.summary}
            </p>
            
            <a 
              href={mag.pdf_url} 
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary w-full justify-center gap-2"
            >
              <Download size={16} />
              Download PDF
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

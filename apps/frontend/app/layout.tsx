import type { Metadata } from 'next';
import './globals.css';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { QueryProvider } from '@/components/providers/QueryProvider';
import { Toaster } from 'sonner';

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'https://bharatvanguard.news'),
  title: {
    default: 'Bharat Vanguard News (BVN) — AI-Powered News Platform',
    template: '%s | BVN',
  },
  description:
    'AI-powered news intelligence platform. Collect, analyze, verify, and search news from trusted sources with transparent trust scoring.',
  keywords: ['news', 'AI', 'fact-check', 'news analysis', 'media intelligence', 'news verification'],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://bharatvanguard.news',
    siteName: 'Bharat Vanguard News (BVN)',
    title: 'Bharat Vanguard News (BVN) — AI-Powered News Platform',
    description: 'AI-powered news intelligence with transparent trust scoring.',
    images: [{ url: '/og-image.png', width: 1200, height: 630 }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Bharat Vanguard News (BVN)',
    description: 'India\'s AI-powered news intelligence platform.',
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background text-text-primary antialiased">
        <QueryProvider>
          {/* Background ambient glow */}
          <div className="fixed inset-0 bg-hero-glow pointer-events-none z-0" aria-hidden />

          <div className="relative z-10 flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-1 w-full">
              {children}
            </main>
            <Footer />
          </div>

          <Toaster
            position="bottom-right"
            toastOptions={{
              style: {
                background: '#0F1629',
                border: '1px solid #1E2A45',
                color: '#F0F4FF',
              },
            }}
          />
        </QueryProvider>
      </body>
    </html>
  );
}

import type { Metadata } from 'next';
import './globals.css';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { QueryProvider } from '@/components/providers/QueryProvider';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import { Toaster } from 'sonner';
import { Analytics } from '@vercel/analytics/next';

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'https://bharat-vanguard-news.vercel.app'),
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
    url: 'https://bharat-vanguard-news.vercel.app',
    siteName: 'Bharat Vanguard News (BVN)',
    title: 'Bharat Vanguard News (BVN) — AI-Powered News Platform',
    description: 'AI-powered news intelligence with transparent trust scoring.',
    images: [{ url: '/og-image.png', width: 1200, height: 630 }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Bharat Vanguard News (BVN)',
    description: 'AI-powered news intelligence platform.',
    images: ['/og-image.png'],
  },
  verification: {
    google: 'google18ad3ba05cc7db59',
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased min-h-screen flex flex-col font-sans transition-colors duration-300">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <QueryProvider>
            <Navbar />
            <main className="flex-1 w-full relative pt-16">
              {/* Global gradient background effect */}
              <div className="absolute top-0 inset-x-0 h-96 bg-hero-glow -z-10 opacity-60 dark:opacity-40" />
              {children}
            </main>
            <Footer />
            <Toaster position="bottom-right" theme="system" />
          </QueryProvider>
        </ThemeProvider>
        <Analytics />
      </body>
    </html>
  );
}

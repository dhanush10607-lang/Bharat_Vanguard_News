/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['lucide-react', 'recharts'],
  },
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.bbci.co.uk' },
      { protocol: 'https', hostname: '**.bbc.com' },
      { protocol: 'https', hostname: '**.techcrunch.com' },
      { protocol: 'https', hostname: '**.theverge.com' },
      { protocol: 'https', hostname: '**.thehindu.com' },
      { protocol: 'https', hostname: '**.ndtv.com' },
      { protocol: 'https', hostname: '**.aljazeera.com' },
      { protocol: 'https', hostname: '**.reuters.com' },
      { protocol: 'https', hostname: '**.nasa.gov' },
      { protocol: 'https', hostname: 'lh3.googleusercontent.com' },  // Google avatars
      { protocol: 'https', hostname: '**' },  // Allow all for dev
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

module.exports = nextConfig;

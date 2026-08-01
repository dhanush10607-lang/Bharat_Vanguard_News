import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/api/', '/admin/'],
    },
    // Change to your actual domain if different
    sitemap: 'https://bharat-vanguard-news.vercel.app/sitemap.xml',
  };
}

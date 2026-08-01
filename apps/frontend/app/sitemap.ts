import { MetadataRoute } from 'next';
import { articlesApi, eventsApi } from '@/lib/api';

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL || 'https://bharat-vanguard-news.vercel.app';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const routes: MetadataRoute.Sitemap = [
    {
      url: `${BASE_URL}`,
      lastModified: new Date(),
      changeFrequency: 'hourly',
      priority: 1,
    },
    {
      url: `${BASE_URL}/events`,
      lastModified: new Date(),
      changeFrequency: 'hourly',
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/search`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.7,
    },
    {
      url: `${BASE_URL}/analytics`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.7,
    },
  ];

  try {
    // Fetch latest 50 published articles
    const articlesRes = await articlesApi.list({ page: 1, page_size: 50, status: 'published' });
    if (articlesRes && articlesRes.items) {
      const articleRoutes: MetadataRoute.Sitemap = articlesRes.items.map((article) => ({
        url: `${BASE_URL}/news/${article.slug}`,
        lastModified: article.published_time ? new Date(article.published_time) : new Date(),
        changeFrequency: 'daily',
        priority: 0.8,
      }));
      routes.push(...articleRoutes);
    }
  } catch (error) {
    console.error('Failed to fetch articles for sitemap:', error);
  }

  try {
    // Fetch latest 20 events
    const eventsRes = await eventsApi.list({ page: 1, page_size: 20 });
    if (eventsRes && eventsRes.items) {
      const eventRoutes: MetadataRoute.Sitemap = eventsRes.items.map((event) => ({
        url: `${BASE_URL}/events/${event.slug}`,
        lastModified: event.created_at ? new Date(event.created_at) : new Date(),
        changeFrequency: 'daily',
        priority: 0.8,
      }));
      routes.push(...eventRoutes);
    }
  } catch (error) {
    console.error('Failed to fetch events for sitemap:', error);
  }

  return routes;
}

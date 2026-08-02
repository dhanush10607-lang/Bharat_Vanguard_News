import type { Metadata } from 'next';
import { Suspense } from 'react';
import { articlesApi } from '@/lib/api';
import { CategoryFeed } from '@/components/categories/CategoryFeed';
import { capitalize, getCountryFlag } from '@/lib/utils';

interface Props {
  params: { category: string };
}

const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  world:        'International news and global events',
  technology:   'Latest in tech, software, and digital innovation',
  ai:           'Artificial intelligence, machine learning, and automation',
  business:     'Markets, companies, and economic developments',
  science:      'Research breakthroughs, space, and nature',
  health:       'Medicine, public health, and wellness',
  india:        'News from and about India',
  sports:       'Sports, athletics, and competitions',
  entertainment:'Movies, music, culture, and celebrity news',
  politics:     'Political news and governance',
  finance:      'Financial markets, investing, and economics',
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const cat = params.category;
  const desc = CATEGORY_DESCRIPTIONS[cat] || `Latest ${cat} news`;
  return {
    title: `${capitalize(cat)} News`,
    description: desc,
  };
}

export default function CategoryPage({ params }: Props) {
  const category = params.category;
  const description = CATEGORY_DESCRIPTIONS[category] || `Latest ${category} news`;

  return (
    <div className="pt-8 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-1.5">
            {capitalize(category)} News
          </h1>
          <p className="text-text-muted">{description}</p>
        </div>

        <Suspense fallback={null}>
          <CategoryFeed category={category} />
        </Suspense>
      </div>
    </div>
  );
}

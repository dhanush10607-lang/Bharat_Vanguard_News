import asyncio
from sqlalchemy import select, update
from shared.database import AsyncSessionLocal
from shared.models import AISummary, Article, ArticleEntity, Entity
import json

async def main():
    async with AsyncSessionLocal() as db:
        print('Fetching existing AI summaries...')
        result = await db.execute(select(AISummary, Article).join(Article, AISummary.article_id == Article.article_id))
        rows = result.all()
        
        updated_count = 0
        for summary, article in rows:
            needs_update = False
            
            # Calculate reading time if missing
            if not summary.reading_time_min:
                full_text = f'{article.title}. {article.description or ""} {article.content or ""}'
                word_count = len(full_text.split())
                summary.reading_time_min = max(1, round(word_count / 200))
                article.reading_time_min = summary.reading_time_min
                article.word_count = word_count
                needs_update = True
                
            # Calculate keywords if missing
            if not summary.keywords:
                # Fetch top entities for this article
                ent_res = await db.execute(
                    select(Entity.name)
                    .join(ArticleEntity, ArticleEntity.entity_id == Entity.entity_id)
                    .where(ArticleEntity.article_id == article.article_id)
                    .order_by(ArticleEntity.mention_count.desc())
                    .limit(5)
                )
                top_entities = ent_res.scalars().all()
                if top_entities:
                    summary.keywords = top_entities
                    needs_update = True
                    
            if needs_update:
                updated_count += 1
                
        if updated_count > 0:
            print(f'Updating {updated_count} summaries...')
            await db.commit()
            print('Done!')
        else:
            print('All summaries are already populated!')

if __name__ == '__main__':
    asyncio.run(main())

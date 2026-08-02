import asyncio
from sqlalchemy import select, update
from shared.database import AsyncSessionLocal
from shared.models import Article
import hashlib

async def main():
    async with AsyncSessionLocal() as db:
        print('Fetching existing articles...')
        result = await db.execute(select(Article))
        articles = result.scalars().all()
        
        updated_count = 0
        for article in articles:
            needs_update = False
            
            # Backfill content
            if not article.content:
                article.content = article.description if article.description else article.title
                needs_update = True
                
            # Backfill content_hash
            if not article.content_hash and article.content:
                article.content_hash = hashlib.sha256(article.content.encode('utf-8')).hexdigest()
                needs_update = True
                
            # Backfill is_paywalled
            if article.is_paywalled is None:
                article.is_paywalled = False
                needs_update = True
                
            if needs_update:
                updated_count += 1
                
        if updated_count > 0:
            print(f'Updating {updated_count} articles...')
            await db.commit()
            print('Done!')
        else:
            print('All articles are already populated!')

if __name__ == '__main__':
    asyncio.run(main())

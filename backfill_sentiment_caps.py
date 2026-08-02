import asyncio
from sqlalchemy import select, update
from shared.database import AsyncSessionLocal
from shared.models import Article

async def main():
    async with AsyncSessionLocal() as db:
        print('Fetching existing articles to capitalize sentiment...')
        result = await db.execute(select(Article))
        articles = result.scalars().all()
        
        updated_count = 0
        for article in articles:
            if article.sentiment and not article.sentiment.isupper():
                article.sentiment = article.sentiment.upper()
                updated_count += 1
                
        if updated_count > 0:
            print(f'Updating {updated_count} articles to use capital sentiment...')
            await db.commit()
            print('Done!')
        else:
            print('All articles already have capital sentiments!')

if __name__ == '__main__':
    asyncio.run(main())

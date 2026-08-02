import asyncio
import httpx
import trafilatura
import hashlib
from sqlalchemy import select, delete
from shared.database import AsyncSessionLocal
from shared.models import Article, AISummary, ArticleStatus

async def main():
    async with AsyncSessionLocal() as db:
        print('Fetching existing articles...')
        result = await db.execute(select(Article))
        articles = result.scalars().all()
        
        updated_count = 0
        async with httpx.AsyncClient(timeout=15.0) as client:
            for article in articles:
                # Check if content is likely just the description fallback
                content_len = len(article.content.split()) if article.content else 0
                desc_len = len(article.description.split()) if article.description else 0
                
                # If content is identical to description or very short, it means it's missing the full text
                if not article.content or article.content == article.description or content_len < 100:
                    print(f'Scraping full text for: {article.title[:50]}...')
                    try:
                        resp = await client.get(article.url, follow_redirects=True)
                        if resp.status_code == 200:
                            extracted = trafilatura.extract(resp.text, include_comments=False, include_tables=False)
                            
                            if extracted and len(extracted.split()) > desc_len:
                                article.content = extracted
                                article.content_hash = hashlib.sha256(extracted.encode("utf-8")).hexdigest()
                                
                                # Set back to RAW so the NLP Worker will re-summarize the new full text!
                                article.status = ArticleStatus.RAW
                                
                                # Delete old AI summary based on the short description
                                await db.execute(delete(AISummary).where(AISummary.article_id == article.article_id))
                                
                                updated_count += 1
                                print(f'  -> Success! Extracted {len(extracted.split())} words. Queued for AI re-processing.')
                            else:
                                print('  -> Could not extract more text than description.')
                    except Exception as e:
                        print(f'  -> Failed to fetch URL: {e}')
                        
        if updated_count > 0:
            print(f'\nSaving {updated_count} updated articles...')
            await db.commit()
            print('Done! The NLP worker will automatically pick these up and re-generate proper AI summaries based on the full text!')
        else:
            print('\nAll articles already have full content!')

if __name__ == '__main__':
    asyncio.run(main())

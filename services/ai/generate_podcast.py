import asyncio

from sqlalchemy import select
from shared.database import AsyncSessionLocal
from shared.models import Article, AISummary, ArticleStatus

async def main():
    async with AsyncSessionLocal() as db:
        # Get top 5 most recent processed/published articles
        stmt = (
            select(Article)
            .where(Article.status.in_([ArticleStatus.PROCESSED, ArticleStatus.PUBLISHED]))
            .order_by(Article.published_time.desc())
            .limit(5)
        )
        result = await db.execute(stmt)
        articles = result.scalars().all()
        
        if not articles:
            print("No articles found for the podcast.")
            return

        # Fetch summaries for these articles
        article_ids = [a.article_id for a in articles]
        summary_stmt = select(AISummary).where(AISummary.article_id.in_(article_ids))
        summary_result = await db.execute(summary_stmt)
        summaries = {s.article_id: s for s in summary_result.scalars().all()}

        # Build the script
        script_parts = [
            "Good morning! Here is your daily news briefing from Bharat Vanguard News."
        ]
        
        for idx, article in enumerate(articles, 1):
            summary = summaries.get(article.article_id)
            if not summary or not summary.summary_medium:
                continue
                
            script_parts.append(f"Story number {idx}.")
            script_parts.append(article.title + ".")
            script_parts.append(summary.summary_medium)
            
        script_parts.append("That's all for today. Stay informed, and have a great day!")
        
        full_script = "\n\n".join(script_parts)
        print("Generated Script:\n", full_script)
        
        # Ensure podcast directory exists
        import os
        podcast_dir = "apps/frontend/public/podcast"
        os.makedirs(podcast_dir, exist_ok=True)
        
        output_file = os.path.join(podcast_dir, "latest.mp3")
        
        # Use gTTS (Google Text-to-Speech) which is reliable and free
        from gtts import gTTS
        
        print(f"Generating audio with gTTS...")
        tts = gTTS(text=full_script, lang='en', tld='com.au')  # Australian accent for a unique professional tone
        
        # Save blocking call in a thread
        await asyncio.to_thread(tts.save, output_file)
        
        print(f"Podcast saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())

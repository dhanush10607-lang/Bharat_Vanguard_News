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

        # Determine time of day for greeting
        import datetime
        import json
        import os
        import glob

        now = datetime.datetime.now()
        hour = now.hour
        
        if hour < 12:
            greeting = "Good morning!"
            edition = "Morning"
        elif hour < 17:
            greeting = "Good afternoon!"
            edition = "Afternoon"
        else:
            greeting = "Good evening!"
            edition = "Evening"

        # Build the script
        script_parts = [
            f"{greeting} Here is your {edition} news briefing from Bharat Vanguard News."
        ]
        
        for idx, article in enumerate(articles, 1):
            summary = summaries.get(article.article_id)
            if not summary or not summary.summary_medium:
                continue
                
            script_parts.append(f"News Headline {idx}.")
            script_parts.append(article.title + ".")
            script_parts.append(summary.summary_medium)
            
        script_parts.append("That's all for now. Stay informed, and have a great day!")
        
        full_script = "\n\n".join(script_parts)
        print("Generated Script:\n", full_script)
        
        # Ensure podcast directory exists
        podcast_dir = "apps/frontend/public/podcast"
        os.makedirs(podcast_dir, exist_ok=True)
        
        # Generate filenames
        timestamp = now.strftime("%Y-%m-%d_%H-%M")
        filename = f"podcast_{timestamp}_{edition}.mp3"
        output_file = os.path.join(podcast_dir, filename)
        latest_file = os.path.join(podcast_dir, "latest.mp3")
        
        # Use edge-tts (Microsoft Azure Neural TTS) which is highly reliable and free
        import edge_tts
        
        print("Generating audio with edge-tts...")
        # Natasha is a professional sounding Australian Neural voice
        voice = "en-AU-NatashaNeural"
        communicate = edge_tts.Communicate(full_script, voice)
        
        # Save directly asynchronously
        await communicate.save(output_file)
        
        # Copy to latest.mp3 for backward compatibility
        import shutil
        shutil.copy2(output_file, latest_file)
        
        # Update history JSON
        history_file = os.path.join(podcast_dir, "podcast_history.json")
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except Exception:
                pass
                
        # Add new entry
        display_date = now.strftime("%b %d")
        history.insert(0, {
            "title": f"{edition} Briefing - {display_date}",
            "filename": filename,
            "date": now.isoformat(),
            "timestamp": now.timestamp()
        })
        
        # Prune old files (> 7 days)
        seven_days_ago = now.timestamp() - (7 * 24 * 3600)
        
        # Filter history to keep only last 7 days
        pruned_history = [entry for entry in history if entry.get("timestamp", 0) > seven_days_ago]
        
        # Delete old MP3s physically
        kept_files = {entry["filename"] for entry in pruned_history}
        kept_files.add("latest.mp3")
        
        for mp3_path in glob.glob(os.path.join(podcast_dir, "*.mp3")):
            mp3_file = os.path.basename(mp3_path)
            if mp3_file not in kept_files:
                try:
                    os.remove(mp3_path)
                    print(f"Deleted old podcast: {mp3_file}")
                except Exception as e:
                    print(f"Failed to delete {mp3_file}: {e}")
                    
        # Save history back
        with open(history_file, 'w') as f:
            json.dump(pruned_history, f, indent=2)
        
        print(f"Podcast saved to {output_file} and history updated.")

if __name__ == "__main__":
    asyncio.run(main())

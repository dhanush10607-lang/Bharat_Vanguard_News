import asyncio
import json
import sys
from pathlib import Path
from sqlalchemy import select

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database import AsyncSessionLocal
from shared.models import Article, AISummary, ArticleStatus

async def export_data():
    output_file = Path("training_dataset.jsonl")
    
    print("Starting secure data export for AI training...")
    
    async with AsyncSessionLocal() as db:
        # Fetch articles that were successfully processed and have an AI summary
        result = await db.execute(
            select(Article, AISummary)
            .join(AISummary, Article.article_id == AISummary.article_id)
            .where(Article.status == ArticleStatus.PUBLISHED)
        )
        rows = result.all()
        
        if not rows:
            print("No processed articles found in the database. Ensure the NLP pipeline has processed some articles first.")
            return

        exported_count = 0
        with open(output_file, "w", encoding="utf-8") as f:
            for article, summary in rows:
                body_text = article.content or article.description
                if not body_text or not summary.summary_medium:
                    continue
                
                # Format as an OpenAI/Open-Source standard Chat Completion message
                # This format works with free local fine-tuning frameworks like Unsloth, HuggingFace, etc.
                training_example = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional news AI. Given a raw news article, you must provide a concise summary, extract key bullet points, and identify relevant keywords."
                        },
                        {
                            "role": "user",
                            "content": f"Title: {article.title}\n\nArticle Body:\n{body_text}"
                        },
                        {
                            "role": "assistant",
                            "content": f"Summary: {summary.summary_medium}\n\nBullet Points:\n- " + "\n- ".join(summary.summary_bullets or []) + f"\n\nKeywords: {', '.join(summary.keywords or [])}"
                        }
                    ]
                }
                
                f.write(json.dumps(training_example, ensure_ascii=False) + "\n")
                exported_count += 1
                
        print(f"Success! Exported {exported_count} articles to {output_file.absolute()}")
        print("You can use this JSONL file to fine-tune free models like Llama 3 or Mistral using tools like Unsloth or Axolotl.")

if __name__ == "__main__":
    asyncio.run(export_data())

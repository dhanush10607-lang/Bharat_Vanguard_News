import asyncio
import os
from sqlalchemy.future import select
from deep_translator import GoogleTranslator

# Ensure we import from the right place depending on where this is run
try:
    from shared.database import AsyncSessionLocal
    from shared.models.articles import Article
    from shared.models.ai_summaries import AISummary
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from shared.database import AsyncSessionLocal
    from shared.models.articles import Article
    from shared.models.ai_summaries import AISummary

TARGET_LANGUAGES = ['hi', 'ta', 'te', 'bn'] # Hindi, Tamil, Telugu, Bengali

async def translate_summaries():
    print("Starting translation of AI Summaries...")
    async with AsyncSessionLocal() as db:
        # Get summaries that haven't been translated to Hindi yet (as a proxy for all)
        # Using a simple check: where translations is null or doesn't have 'hi' key
        stmt = select(AISummary).order_by(AISummary.created_at.desc()).limit(20)
        result = await db.execute(stmt)
        summaries = result.scalars().all()
        
        updated_count = 0
        
        for summary in summaries:
            translations = summary.translations or {}
            
            needs_update = False
            
            for lang in TARGET_LANGUAGES:
                if lang not in translations:
                    translations[lang] = {}
                
                if summary.summary_short and "summary_short" not in translations[lang]:
                    try:
                        translated = GoogleTranslator(source='auto', target=lang).translate(summary.summary_short)
                        translations[lang]["summary_short"] = translated
                        needs_update = True
                        print(f"Translated to {lang}: {summary.summary_short[:30]}...")
                    except Exception as e:
                        print(f"Failed to translate to {lang}: {e}")
            
            if needs_update:
                summary.translations = translations
                updated_count += 1
                
        if updated_count > 0:
            await db.commit()
            print(f"Successfully updated translations for {updated_count} summaries.")
        else:
            print("No new translations needed.")

if __name__ == "__main__":
    asyncio.run(translate_summaries())

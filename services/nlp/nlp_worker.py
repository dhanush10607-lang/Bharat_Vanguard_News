"""
TruthLens AI — NLP Pipeline Worker
Fetches raw articles from the database and runs them through the NLP pipeline:
- Language detection
- Sentiment analysis
- Topic classification
- Semantic embeddings
- Named entity extraction (NER)
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Setup path so we can import from shared/
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database import AsyncSessionLocal
from shared.models import Article, ArticleStatus, SentimentLabel, ArticleEmbedding, Entity, ArticleEntity, AISummary
from shared.utils.slugify import make_slug

# Import NLP services
from services.nlp.language_detector import detect_language
from services.nlp.entity_extractor import get_entity_extractor
from services.nlp.topic_classifier import get_topic_classifier
from services.nlp.sentiment_analyzer import get_sentiment_analyzer
from services.nlp.embedder import get_embedder
from services.summarization.summarizer import get_summarizer

from services.deduplication.event_manager import EventManager
from services.trust_scorer.trust_scorer import get_trust_scorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nlp.worker")

class NLPWorker:
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        logger.info("Initializing NLP Worker (loading models...)")
        # Initialize singletons to load models into memory
        self.entity_extractor = get_entity_extractor()
        self.topic_classifier = get_topic_classifier()
        self.sentiment_analyzer = get_sentiment_analyzer()
        self.embedder = get_embedder()
        self.summarizer = get_summarizer()
        self.event_manager = EventManager(similarity_threshold=0.85)
        self.trust_scorer = get_trust_scorer()
        logger.info("NLP Worker models loaded.")

    async def get_raw_articles(self, db: AsyncSession) -> List[Article]:
        """Fetch a batch of unprocessed articles."""
        result = await db.execute(
            select(Article)
            .where(Article.status == ArticleStatus.RAW)
            .limit(self.batch_size)
        )
        return list(result.scalars().all())

    async def _process_article(self, db: AsyncSession, article: Article):
        """Process a single article through the pipeline."""
        logger.info(f"Processing article {article.article_id}: {article.title[:50]}...")
        
        # 1. Combine text for analysis
        full_text = f"{article.title}. {article.description or ''} {article.content or ''}"
        
        # 2. Language Detection
        if not article.language or article.language == "unknown":
            article.language = detect_language(full_text)
            
        # Only process English for now to save resources
        if article.language != "en":
            article.status = ArticleStatus.PROCESSED
            return

        # 3. Sentiment Analysis
        if not article.sentiment:
            sentiment_result = self.sentiment_analyzer.analyze(full_text)
            try:
                article.sentiment = SentimentLabel(sentiment_result["sentiment"])
            except ValueError:
                article.sentiment = SentimentLabel.NEUTRAL

        # 4. Topic Classification
        if not article.category:
            topic_result = self.topic_classifier.classify(full_text)
            article.category = topic_result["category"]

        # 5. Embeddings (skip if exists)
        exists = await db.execute(
            select(ArticleEmbedding.embedding_id).where(ArticleEmbedding.article_id == article.article_id)
        )
        if not exists.scalar_one_or_none():
            vector = self.embedder.generate_embedding(full_text)
            embedding = ArticleEmbedding(
                article_id=article.article_id,
                vector=vector
            )
            db.add(embedding)

        # 6. Entity Extraction
        entities = self.entity_extractor.extract_entities(full_text)
        
        for ent_data in entities:
            # Check if entity already exists
            slug = make_slug(f"{ent_data['type']}-{ent_data['name']}")
            
            ent_result = await db.execute(
                select(Entity).where(Entity.slug == slug)
            )
            entity = ent_result.scalar_one_or_none()
            
            if not entity:
                entity = Entity(
                    name=ent_data["name"],
                    slug=slug,
                    type=ent_data["type"]
                )
                db.add(entity)
                await db.flush() # get ID
            
            # Link article and entity
            article_entity = ArticleEntity(
                article_id=article.article_id,
                entity_id=entity.entity_id,
                mention_count=ent_data["count"]
            )
            db.add(article_entity)
            
            # Increment global entity count
            entity.article_count += 1

        # 7. Summarization
        # Generate multi-level summary and save to AISummary
        summary_exists = await db.execute(
            select(AISummary.summary_id).where(AISummary.article_id == article.article_id)
        )
        if not summary_exists.scalar_one_or_none():
            logger.info(f"Generating summary for article {article.article_id}...")
            summary_result = self.summarizer.summarize_article(full_text)
            
            ai_summary = AISummary(
                article_id=article.article_id,
                summary_short=summary_result["short"],
                summary_medium=summary_result["medium"],
                summary_bullets=summary_result["bullets"],
                language=article.language
            )
            db.add(ai_summary)

        # 8. Cluster into Events
        # We pass the newly created embedding object
        event = await self.event_manager.cluster_article(db, article, embedding)

        # 9. Trust Scoring
        # Generates transparency score based on publisher rep + event cross-confirmation
        await self.trust_scorer.score_article(db, article, event)

        # Mark as Published (ready for frontend)
        article.status = ArticleStatus.PUBLISHED
        logger.info(f"Finished processing article {article.article_id}")

    async def run_batch(self):
        """Run one batch of processing."""
        async with AsyncSessionLocal() as db:
            articles = await self.get_raw_articles(db)
            if not articles:
                logger.info("No raw articles found. Pipeline idle.")
                return 0
                
            logger.info(f"Found {len(articles)} raw articles for NLP processing.")
            
            for article in articles:
                try:
                    await self._process_article(db, article)
                    await db.commit() # commit each article so a crash doesn't lose all
                except Exception as e:
                    logger.error(f"Error processing article {article.article_id}: {e}")
                    await db.rollback()
                    article.status = ArticleStatus.FAILED
                    db.add(article)
                    await db.commit()
            
            return len(articles)

async def main():
    worker = NLPWorker(batch_size=5) # Small batch for local test
    await worker.run_batch()

if __name__ == "__main__":
    asyncio.run(main())

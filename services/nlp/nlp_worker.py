"""
Bharat Vanguard News (BVN) — NLP Pipeline Worker
Fetches raw articles from the database and runs them through the NLP pipeline:
- Language detection
- Sentiment analysis
- Topic classification
- Semantic embeddings
- Named entity extraction (NER)
- AI Summarization
- Event Clustering
- Trust Scoring
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sa_update
from sqlalchemy.orm import selectinload

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
        self.entity_extractor = get_entity_extractor()
        self.topic_classifier = get_topic_classifier()
        self.sentiment_analyzer = get_sentiment_analyzer()
        self.embedder = get_embedder()
        self.summarizer = get_summarizer()
        self.event_manager = EventManager(similarity_threshold=0.85)
        self.trust_scorer = get_trust_scorer()
        logger.info("NLP Worker models loaded.")

    async def get_raw_article_ids(self) -> List[str]:
        """Fetch IDs of a batch of unprocessed articles as plain strings."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Article.article_id)
                .where(Article.status == ArticleStatus.RAW)
                .limit(self.batch_size)
            )
            return [str(row[0]) for row in result.all()]

    async def _process_article(self, db: AsyncSession, article: Article):
        """Process a single article through the NLP pipeline."""
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
        embedding = None
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
        
        seen_slugs = set()
        for ent_data in entities:
            slug = make_slug(f"{ent_data['type']}-{ent_data['name']}")
            
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            ent_result = await db.execute(
                select(Entity).where(Entity.slug == slug)
            )
            entity = ent_result.scalar_one_or_none()

            if not entity:
                from sqlalchemy.dialects.postgresql import insert as pg_insert
                # Use UPSERT to avoid concurrency IntegrityError
                stmt = pg_insert(Entity).values(
                    name=ent_data["name"],
                    slug=slug,
                    type=ent_data["type"]
                ).on_conflict_do_nothing(index_elements=['slug']).returning(Entity.entity_id)
                
                res = await db.execute(stmt)
                entity_id = res.scalar_one_or_none()
                
                if not entity_id:
                    # Concurrently inserted, fetch it
                    ent_result = await db.execute(select(Entity.entity_id).where(Entity.slug == slug))
                    entity_id = ent_result.scalar_one()
            else:
                entity_id = entity.entity_id

            article_entity = ArticleEntity(
                article_id=article.article_id,
                entity_id=entity_id,
                mention_count=ent_data["count"]
            )
            db.add(article_entity)
            
            if entity:
                entity.article_count += 1
            else:
                # Update article_count directly
                await db.execute(
                    Entity.__table__.update().where(Entity.entity_id == entity_id).values(article_count=Entity.article_count + 1)
                )

        # 7. Summarization
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

            # Assign sentiment and category to the article itself
            article.sentiment = summary_result.get("sentiment", "neutral")
            article.category = summary_result.get("category", "General")

        # 8. Cluster into Events
        event = await self.event_manager.cluster_article(db, article, embedding)

        # 9. Trust Scoring
        await self.trust_scorer.score_article(db, article, event)

        # Mark as Published (ready for frontend)
        article.status = ArticleStatus.PUBLISHED
        logger.info(f"Finished processing article {article.article_id}")

    async def run_batch(self):
        """
        Run one batch of processing.
        Each article gets its own isolated database session so a failure
        in one article never corrupts the processing of others.
        """
        article_ids = await self.get_raw_article_ids()

        if not article_ids:
            logger.info("No raw articles found. Pipeline idle.")
            return 0

        logger.info(f"Found {len(article_ids)} raw articles for NLP processing.")

        for article_id in article_ids:
            async with AsyncSessionLocal() as db:
                try:
                    result = await db.execute(
                        select(Article)
                        .options(selectinload(Article.publisher))
                        .where(Article.article_id == UUID(article_id))
                    )
                    article = result.scalar_one_or_none()
                    if article is None:
                        continue
                    await self._process_article(db, article)
                    await db.commit()
                except Exception as e:
                    logger.error(f"Error processing article {article_id}: {e}")
                    try:
                        await db.rollback()
                        # Open a brand-new session to safely mark the article as FAILED
                        async with AsyncSessionLocal() as fail_db:
                            await fail_db.execute(
                                sa_update(Article)
                                .where(Article.article_id == UUID(article_id))
                                .values(status=ArticleStatus.FAILED)
                            )
                            await fail_db.commit()
                    except Exception as inner_e:
                        logger.error(f"Failed to mark article {article_id} as FAILED: {inner_e}")

        return len(article_ids)


async def main():
    import time

    # How often to check for new raw articles (in seconds)
    POLL_INTERVAL_SECONDS = 60  # Check every 60 seconds

    worker = NLPWorker(batch_size=5)
    logger.info(f"NLP Worker started. Polling every {POLL_INTERVAL_SECONDS}s for new articles...")

    while True:
        processed = await worker.run_batch()
        if processed > 0:
            logger.info(f"Batch complete. Processed {processed} articles. Checking again in {POLL_INTERVAL_SECONDS}s...")
        else:
            logger.info(f"No new articles found. Sleeping {POLL_INTERVAL_SECONDS}s...")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())

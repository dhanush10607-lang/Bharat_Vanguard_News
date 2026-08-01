"""
TruthLens AI — Event Manager
Clusters related articles into "Events" (developing stories).
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.models import Article, Event, EventArticle, ArticleEmbedding
from shared.utils.slugify import make_slug
from services.deduplication.dedup_engine import DedupEngine

logger = logging.getLogger("dedup.event_manager")

class EventManager:
    def __init__(self, similarity_threshold: float = 0.85):
        self.dedup_engine = DedupEngine(similarity_threshold=similarity_threshold)

    async def cluster_article(self, db: AsyncSession, article: Article, embedding: ArticleEmbedding) -> Optional[Event]:
        """
        Attempts to cluster a newly processed article into an Event.
        If similar articles are found, it adds it to an existing Event,
        or creates a new Event grouping them.
        """
        if not embedding or not embedding.vector:
            return None

        # 1. Find similar articles
        similar_items = await self.dedup_engine.find_similar_articles(
            db, 
            target_vector=embedding.vector, 
            limit=3,
            exclude_article_id=article.article_id
        )

        if not similar_items:
            # No similar articles found yet. Remains unclustered.
            return None

        # Sort by most similar first
        similar_items.sort(key=lambda x: x[1], reverse=True)
        best_match_emb, best_score = similar_items[0]

        # 2. Check if the best match is already part of an Event
        # Get the EventArticle link for the best match
        ea_result = await db.execute(
            select(EventArticle).where(EventArticle.article_id == best_match_emb.article_id)
        )
        existing_ea = ea_result.scalar_one_or_none()

        if existing_ea:
            # Add to existing event
            event_id = existing_ea.event_id
            
            # Make sure this article isn't already in this event
            check_exist = await db.execute(
                select(EventArticle).where(
                    EventArticle.event_id == event_id,
                    EventArticle.article_id == article.article_id
                )
            )
            if not check_exist.scalar_one_or_none():
                new_link = EventArticle(
                    event_id=event_id,
                    article_id=article.article_id,
                    similarity_score=best_score,
                    is_primary=False
                )
                db.add(new_link)
                
                # Update event article count
                ev_result = await db.execute(select(Event).where(Event.event_id == event_id))
                event = ev_result.scalar_one()
                event.article_count += 1
                
                logger.info(f"Added article {article.article_id} to existing Event {event.event_id}")
                return event
            
            return None

        else:
            # 3. Neither article is in an Event. Create a new Event.
            # We use the title of the older/primary article as the Event title.
            
            # Fetch the actual article for the best match
            match_article_result = await db.execute(
                select(Article).where(Article.article_id == best_match_emb.article_id)
            )
            match_article = match_article_result.scalar_one()
            
            event_title = match_article.title
            event_slug = make_slug(event_title)
            
            # Ensure unique slug
            base_slug = event_slug
            counter = 1
            while True:
                slug_check = await db.execute(select(Event).where(Event.slug == event_slug))
                if not slug_check.scalar_one_or_none():
                    break
                event_slug = f"{base_slug}-{counter}"
                counter += 1

            new_event = Event(
                title=event_title,
                slug=event_slug,
                category=match_article.category or article.category,
                country=match_article.country or article.country,
                article_count=2,
                sentiment=match_article.sentiment # inherit sentiment
            )
            db.add(new_event)
            await db.flush() # get ID
            
            # Link both articles
            link1 = EventArticle(
                event_id=new_event.event_id,
                article_id=match_article.article_id,
                similarity_score=1.0, # Primary
                is_primary=True
            )
            link2 = EventArticle(
                event_id=new_event.event_id,
                article_id=article.article_id,
                similarity_score=best_score,
                is_primary=False
            )
            
            db.add(link1)
            db.add(link2)
            
            logger.info(f"Created new Event {new_event.event_id} from articles {match_article.article_id} and {article.article_id}")
            return new_event

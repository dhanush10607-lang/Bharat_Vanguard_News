"""
Bharat Vanguard News (BVN) — Deduplication Engine
Uses pgvector to perform fast semantic similarity search across article embeddings.
Helps cluster articles into Events and prevent duplicates.
"""
import logging
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.models import ArticleEmbedding

logger = logging.getLogger("dedup.engine")

class DedupEngine:
    def __init__(self, similarity_threshold: float = 0.85):
        # Default 0.85 means very similar topics.
        # pgvector uses distance, so distance = 1 - similarity.
        self.similarity_threshold = similarity_threshold
        self.max_distance = 1.0 - self.similarity_threshold

    async def find_similar_articles(
        self, 
        db: AsyncSession, 
        target_vector: list[float], 
        limit: int = 5,
        exclude_article_id=None
    ) -> List[Tuple[ArticleEmbedding, float]]:
        """
        Finds articles with embeddings similar to the target vector.
        Returns a list of tuples: (ArticleEmbedding, similarity_score).
        """
        # cosine_distance is an operator provided by pgvector
        distance_col = ArticleEmbedding.vector.cosine_distance(target_vector).label("distance")
        
        query = select(ArticleEmbedding, distance_col).where(
            ArticleEmbedding.vector.cosine_distance(target_vector) < self.max_distance
        )
        
        if exclude_article_id:
            query = query.where(ArticleEmbedding.article_id != exclude_article_id)
            
        query = query.order_by("distance").limit(limit)
        
        result = await db.execute(query)
        rows = result.all()
        
        similar_items = []
        for embedding, distance in rows:
            # Convert distance back to similarity score
            similarity = 1.0 - float(distance)
            similar_items.append((embedding, similarity))
            
        return similar_items

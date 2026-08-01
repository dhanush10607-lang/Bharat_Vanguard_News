"""
TruthLens AI — Embedder
Generates semantic embeddings for articles using sentence-transformers (all-MiniLM-L6-v2).
These embeddings are stored in PostgreSQL using pgvector for similarity search.
"""
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("nlp.embedder")

class Embedder:
    def __init__(self):
        logger.info("Loading Sentence Transformer model (all-MiniLM-L6-v2)...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        self.vector_dim = 384  # Dimension for all-MiniLM-L6-v2
        logger.info(f"Sentence Transformer loaded (dim={self.vector_dim}).")

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generates a fixed-length vector embedding for the input text.
        """
        if not text or not text.strip():
            return [0.0] * self.vector_dim
            
        try:
            # We encode the text and convert to a native Python list of floats for pgvector
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return [0.0] * self.vector_dim

# Singleton
_embedder = None

def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder

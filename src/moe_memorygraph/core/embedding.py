from sentence_transformers import SentenceTransformer
from moe_memorygraph.core.config import settings

class EmbeddingService:
    """
    Singleton service to handle text embedding generation.
    Loads the model once and reuses it for high performance.
    """
    def __init__(self):
        print(f"🧠 Loading embedding model: {settings.EMBEDDING_MODEL}...")
        # Downloads model to local cache on first run (approx 80MB)
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed_query(self, text: str) -> list[float]:
        """Generates a vector embedding for a single string."""
        if not text:
            return []
        # Convert numpy array to standard python list for pgvector compatibility
        return self.model.encode(text).tolist()

# Create a single instance to be imported elsewhere
embedder = EmbeddingService()
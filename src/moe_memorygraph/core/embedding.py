from sentence_transformers import SentenceTransformer
from moe_memorygraph.core.config import settings

class EmbeddingService:
    """
    Singleton service to handle text embedding generation.
    Loads the model once and reuses it.
    """
    def __init__(self):
        # LOGIC: Loading an AI model takes time and RAM (approx 100MB).
        # We do this inside __init__ so it happens ONLY ONCE when the app starts.
        print(f"🧠 Loading embedding model: {settings.EMBEDDING_MODEL}...")
        
        # SYNTAX: 'SentenceTransformer' is the library that runs the model.
        # 'settings.EMBEDDING_MODEL' pulls the string "sentence-transformers/all-MiniLM-L6-v2" 
        # from your config.py file.
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed_query(self, text: str) -> list[float]:
        """Generates a vector embedding for a single string."""
        
        # LOGIC: Safety Check. If you try to embed an empty string, the model might crash
        # or return garbage. We catch it early and return an empty list.
        if not text:
            return []
            
        # SYNTAX: self.model.encode(text)
        # This function runs the neural network. It returns a 'NumPy Array' (optimized C code).
        # PostgreSQL does not understand NumPy. It only understands standard Python Lists.
        # .tolist() converts the C-array into a regular Python [0.1, 0.2...] list.
        return self.model.encode(text).tolist()

# LOGIC: The Singleton Pattern
# We create the variable 'embedder' right here at the bottom.
# Any other file that imports 'embedder' will share THIS exact instance.
# This prevents your app from loading the model 50 times and crashing your RAM.
embedder = EmbeddingService()
from sentence_transformers import SentenceTransformer
import torch

# --- 1. Model Initialization (Singleton) ---
# We load the model once when the module is imported to save memory.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Detect Hardware
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    print(f"🚀 GPU Detected: Running on {torch.cuda.get_device_name(0)}")
else:
    print("⚠️ GPU Not Detected: Running on CPU (Slower)")

print(f"🧠 Loading embedding model: {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME, device=device)

# --- 2. The Missing Function ---
async def embed_text(text: str) -> list[float]:
    """
    Converts a string of text into a high-dimensional vector.
    
    Args:
        text (str): The input text to embed.
        
    Returns:
        list[float]: A list of floats representing the embedding (size 384 for MiniLM).
    """
    if not text:
        return []

    # Encode returns a numpy array; convert to standard list for PostgreSQL/pgvector
    # Note: For very high loads, this CPU-bound task should ideally run in an executor,
    # but for this agentic graph, running it directly is fine.
    embedding = model.encode(text, convert_to_numpy=True)
    
    return embedding.tolist()
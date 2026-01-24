# SYNTAX: Import 'torch' (PyTorch).
# LOGIC: This is the heavy math engine deep underneath. We need it directly 
# so we can ask the hardware: "Do you have a GPU?"
import torch

from sentence_transformers import SentenceTransformer
from moe_memorygraph.core.config import settings

class EmbeddingService:
    """
    Singleton service to handle text embedding generation.
    Automatically detects GPU (CUDA/MPS) or CPU for maximum performance.
    """
    
    def __init__(self):
        # --- HARDWARE DETECTION LOGIC ---
        
        # SYNTAX: torch.cuda.is_available()
        # LOGIC: Check for NVIDIA GPUs first. These are the gold standard for AI.
        # If found, we set the device flag to "cuda".
        if torch.cuda.is_available():
            self.device = "cuda"
            print(f"🚀 GPU Detected: Running on NVIDIA CUDA ({torch.cuda.get_device_name(0)})")
            
        # SYNTAX: torch.backends.mps.is_available()
        # LOGIC: Check for Apple Silicon (M1/M2/M3) GPUs. 
        # 'mps' stands for Metal Performance Shaders. 
        elif torch.backends.mps.is_available():
            self.device = "mps"
            print("🍎 GPU Detected: Running on Apple Metal (MPS)")
            
        # LOGIC: Fallback. If no fancy hardware is found, use the standard CPU.
        # It's slower (approx 20x), but it guarantees the code won't crash.
        else:
            self.device = "cpu"
            print("🐢 No GPU detected: Running on Standard CPU")

        print(f"🧠 Loading embedding model: {settings.EMBEDDING_MODEL}...")
        
        # SYNTAX: SentenceTransformer(..., device=self.device)
        # LOGIC: The 'device' parameter is critical.
        # It tells the library to load the 400MB model weights directly into VRAM (Video RAM)
        # if a GPU is used. If we didn't do this, the model would sit in slow RAM 
        # while the GPU sat idle.
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL, device=self.device)

    def embed_query(self, text: str) -> list[float]:
        """Generates a vector embedding for a single string."""
        
        # LOGIC: Input Guard.
        # If we feed an empty string to the model, it wastes computation 
        # or returns a garbage vector. We catch it early.
        if not text:
            return []
        
        # SYNTAX: self.model.encode(...)
        # LOGIC: 
        # 1. We pass the text to the neural network.
        # 2. 'device=self.device': We must remind the function to use the GPU for *this specific calculation*.
        # 3. .tolist(): The model returns a 'NumPy Array' (C++ optimized format).
        #    PostgreSQL cannot understand NumPy. It needs a standard Python List [0.1, 0.2...].
        #    This method performs that conversion.
        return self.model.encode(text, device=self.device).tolist()

# SYNTAX: Singleton Instantiation
# LOGIC: We create the variable 'embedder' here at the module level.
# This means the model is loaded ONLY ONCE when you start the app.
# Any file that says 'from core.embedding import embedder' just borrows this existing object.
embedder = EmbeddingService()
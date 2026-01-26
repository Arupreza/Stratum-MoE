import asyncio
import sys
import os

# Fix path to ensure imports work regardless of how this is run
sys.path.append(os.getcwd())

from src.moe_memorygraph.db.session import async_session_factory
from src.moe_memorygraph.db.models import VectorMemory, SemanticFact
from src.moe_memorygraph.core.embedding import embed_text

async def ingest():
    print("🧠 Starting Hybrid Ingestion (Vector + Semantic)...")
    
    async with async_session_factory() as session:
        # --- 1. Vector Data (Unstructured Text) ---
        texts = [
            "To reset your password, go to Settings > Security and click 'Change Password'.",
            "If you are locked out, contact IT support at support@demo_corp.com.",
            "Password policies require at least 12 characters and one symbol.",
            "Two-factor authentication (2FA) can be enabled in the user profile."
        ]
        
        print(f"   -> Processing {len(texts)} vector items...")
        for text in texts:
            # Create Embedding
            vector = await embed_text(text)
            
            # Create Database Record
            memory = VectorMemory(
                tenant_id="demo_corp",
                content=text,
                embedding=vector,
                metadata_={"source": "manual_ingest"}
            )
            session.add(memory)

        # --- 2. Semantic Data (Structured Facts) ---
        print("   -> Inserting Semantic Facts...")
        
        fact1 = SemanticFact(
            tenant_id="demo_corp",
            entity_name="Password Reset",
            attribute="location",
            value="Settings > Security",
            confidence=1.0
        )
        fact2 = SemanticFact(
            tenant_id="demo_corp",
            entity_name="IT Support",
            attribute="email",
            value="support@demo_corp.com",
            confidence=1.0
        )
        session.add_all([fact1, fact2])
        
        # Commit all changes
        await session.commit()
        
    print("✅ Ingestion Complete! The brain now contains knowledge.")

if __name__ == "__main__":
    asyncio.run(ingest())
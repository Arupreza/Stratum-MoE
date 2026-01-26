from sqlalchemy import select
from moe_memorygraph.db.session import AsyncSessionLocal
from moe_memorygraph.db.models import VectorMemory
from moe_memorygraph.core.embedding import embedder

class VectorRetrievalExpert:
    """
    Expert specialized in semantic search using HNSW vector similarity.
    """
    
    async def search(self, query: str, limit: int = 3) -> list[dict]:
        """
        1. Embeds the query.
        2. Searches DB for nearest neighbors (Cosine Similarity).
        3. Returns formatted results.
        """
        # Guard Clause: Don't search for nothing
        if not query:
            return []

        # 1. Translate User Text -> Vector Math
        query_vector = embedder.embed_query(query)

        # 2. Database Search
        async with AsyncSessionLocal() as session:
            stmt = (
                select(VectorMemory)
                # The HNSW Magic: Order by Distance (Smallest distance = Best Match)
                .order_by(VectorMemory.embedding.cosine_distance(query_vector))
                .limit(limit)
            )
            
            result = await session.execute(stmt)
            memories = result.scalars().all()

            # 3. Format Output for the Agent
            return [
                {
                    "content": mem.content,
                    "intent": mem.metadata_.get("intent"),
                    "category": mem.metadata_.get("category"),
                    "response": mem.metadata_.get("response") 
                }
                for mem in memories
            ]

# Singleton: Initialize once, reuse everywhere
vector_expert = VectorRetrievalExpert()
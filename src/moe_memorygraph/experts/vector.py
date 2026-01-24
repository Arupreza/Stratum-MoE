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
        2. Searches the DB for nearest neighbors.
        3. Returns formatted results.
        """
        if not query:
            return []

        # 1. Convert Text -> Vector
        query_vector = embedder.embed_query(query)

        async with AsyncSessionLocal() as session:
            # 2. Perform Vector Search (Cosine Distance)
            # The operator <=> is "Cosine Distance" in pgvector
            stmt = (
                select(VectorMemory)
                .order_by(VectorMemory.embedding.cosine_distance(query_vector))
                .limit(limit)
            )
            
            result = await session.execute(stmt)
            memories = result.scalars().all()

            # 3. Format Output
            return [
                {
                    "content": mem.content,
                    "score": 0.0,  # Placeholder (pgvector returns distance, not similarity directly in select)
                    "intent": mem.metadata_.get("intent"),
                    "response": mem.metadata_.get("response")
                }
                for mem in memories
            ]

# Singleton Instance
vector_expert = VectorRetrievalExpert()
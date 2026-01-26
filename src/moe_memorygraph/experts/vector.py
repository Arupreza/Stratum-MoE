from sqlalchemy import select
from src.moe_memorygraph.db.session import async_session_factory
from src.moe_memorygraph.db.models import VectorMemory
from src.moe_memorygraph.core.embedding import embed_text

# THIS IS THE FUNCTION PYTHON IS LOOKING FOR
async def search_vector_memory(query: str, limit: int = 5, tenant_id: str = "default"):
    """
    Expert: Performs semantic similarity search using pgvector.
    """
    # 1. Convert text query to vector (embedding)
    #    (This will use the GPU since your logs show CUDA is active)
    query_vector = await embed_text(query)

    async with async_session_factory() as session:
        # 2. Search DB (Cosine Distance)
        #    Note: Ensure pgvector extension is enabled in your DB
        stmt = select(VectorMemory).filter(
            VectorMemory.tenant_id == tenant_id
        ).order_by(
            VectorMemory.embedding.cosine_distance(query_vector)
        ).limit(limit)

        result = await session.execute(stmt)
        memories = result.scalars().all()

        # 3. Format output
        return [
            {
                "content": m.content, 
                "metadata": m.metadata_, 
                "distance": "N/A" 
            }
            for m in memories
        ]
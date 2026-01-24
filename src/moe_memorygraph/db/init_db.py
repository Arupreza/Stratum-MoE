import asyncio
from sqlalchemy import text
# CORRECT: Import from the package name, not 'src'
from moe_memorygraph.db.session import engine
from moe_memorygraph.db.models import Base

async def init_db():
    print("🚀 Starting database initialization...")
    async with engine.begin() as conn:
        print("🔧 Enabling pgvector extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
        print("🏗️  Creating tables (Semantic, Vector, LTM)...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database initialized! Tables created with HNSW support.")

if __name__ == "__main__":
    asyncio.run(init_db())
import asyncio
from src.moe_memorygraph.db.session import engine
from src.moe_memorygraph.db.models import Base

async def reset_db():
    print("⚠️  WARNING: This will DROP all existing data!")
    print("🛠️  Connecting to Database...")
    
    async with engine.begin() as conn:
        # 1. Drop the old tables (Clean Slate)
        print("🔥 Dropping old tables...")
        await conn.run_sync(Base.metadata.drop_all)
        
        # 2. Create the new tables (With HNSW Index)
        print("✨ Creating new tables (Vector + Semantic + HNSW Index)...")
        await conn.run_sync(Base.metadata.create_all)
        
    print("✅ Database Reset Complete. You can now ingest data.")

if __name__ == "__main__":
    asyncio.run(reset_db())
import asyncio
from sqlalchemy import text
# 1. THE TOOLBOX
# We import 'engine' (the connection manager) and 'Base' (the blueprint holder).
from moe_memorygraph.db.session import engine
from moe_memorygraph.db.models import Base

async def init_db():
    print("🚀 Starting database initialization...")
    
    # 2. THE CONNECTION
    # 'engine.begin()' opens a temporary connection to Postgres.
    # It acts like a transaction: if anything fails, it undoes everything.
    async with engine.begin() as conn:
        
        # 3. INSTALLING THE BRAIN (pgvector)
        print("🔧 Enabling pgvector extension...")
        # LOGIC: Standard Postgres doesn't know math or vectors. 
        # We run a raw SQL command to install the 'pgvector' plugin.
        # Without this, the database will crash when we try to create a 'Vector(384)' column.
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
        # 4. BUILDING THE TABLES
        print("🏗️  Creating tables (Semantic, Vector, LTM)...")
        # LOGIC: This is the bridge between Python and SQL.
        # 'Base.metadata' holds a list of all models (like VectorMemory) we defined.
        # 'create_all' translates those Python classes into "CREATE TABLE" SQL commands
        # and runs them instantly.
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database initialized! Tables created with HNSW support.")

# 5. THE START BUTTON
if __name__ == "__main__":
    asyncio.run(init_db())
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from moe_memorygraph.core.config import settings 

# 1. The Engine (Connection Pool Manager)
# This acts as the bridge between Python and the PostgreSQL Database.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,          # Set to True to log every SQL query (for debugging)
    future=True,         # Enforce modern SQLAlchemy 2.0 syntax
    pool_size=20,        # Keep 20 connections open permanently
    max_overflow=10      # Allow 10 extra temporary connections during traffic spikes
)

# 2. The Session Factory (Transaction Creator)
# This factory manufactures new 'Session' objects based on the Engine configuration.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # CRITICAL: Keeps data accessible in RAM after commit
    autoflush=False         # Optimization: Only write to DB when explicitly told
)

# 3. The Dependency (Session Lifeguard)
# This function creates, yields, and guarantees the closing of a session.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.moe_memorygraph.core.config import settings

# 1. Create the Async Database Engine
#    This manages the pool of connections to PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True if you want to see every SQL query in logs
    future=True
)

# 2. Create the Session Factory
#    THIS IS THE OBJECT YOUR CODE IS LOOKING FOR.
#    It generates new database sessions for every request.
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Optional: Helper to get a session (dependency injection style)
async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
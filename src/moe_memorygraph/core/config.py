from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Centralized configuration for the application.
    Reads from .env file or environment variables.
    """
    # Application settings
    PROJECT_NAME: str = "MoE MemoryGraph"
    
    # Database Settings (Matches your Docker Compose setup)
    # 1. FIXED: Removed '?ssl=disable' to prevent asyncpg crash
    # 2. KEPT: '127.0.0.1' to fix the connection refused error
    DATABASE_URL: str = "postgresql+asyncpg://arupreza:0000@127.0.0.1:5432/memorygraph"
    
    # LLM Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Vector Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Load from .env file if available
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
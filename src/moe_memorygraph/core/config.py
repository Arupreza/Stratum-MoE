from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Centralized configuration for the application.
    Reads from .env file or environment variables.
    """
    # Application settings
    PROJECT_NAME: str = "MoE MemoryGraph"
    
    # Database Settings (Matches your Docker Compose setup)
    # Format: postgresql+asyncpg://user:password@host:port/dbname
    DATABASE_URL: str = "postgresql+asyncpg://arupreza:0000@localhost:5432/memorygraph"
    
    # LLM Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Vector Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Load from .env file if available
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
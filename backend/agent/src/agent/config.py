"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://agent:agent_secret@localhost:5432/agent_db"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "agent_memory"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    browser_service_url: str = "http://localhost:3001"
    search_service_url: str = "http://localhost:8080"
    log_level: str = "INFO"
    max_graph_iterations: int = 10
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    attachments_dir: str = "data/attachments"
    client_files_dir: str = "data/client-files"
    default_agent_mode: str = "general"

    @property
    def database_url_sync(self) -> str:
        """Sync SQLAlchemy URL for Alembic (psycopg v3 driver)."""
        url = self.database_url.replace("+asyncpg", "")
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @property
    def database_url_checkpoint(self) -> str:
        """Plain psycopg connection string for LangGraph checkpoints."""
        return self.database_url.replace("+asyncpg", "")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

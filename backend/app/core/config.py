from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration lue depuis les variables d'environnement (ou le fichier .env)."""

    model_config = SettingsConfigDict(
        # .env à la racine du projet (lancement depuis backend/) ou local
        env_file=("../.env", ".env"),
        extra="ignore",
    )

    app_name: str = "SobaAI"

    anthropic_api_key: str | None = None
    claude_model: str = "claude-sonnet-5-5"
    claude_effort: str = "low"
    claude_max_tokens: int = 16000

    database_url: str = "postgresql+asyncpg://soba:soba@localhost:5432/sobaai"

    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

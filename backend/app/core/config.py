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

    # Clé de signature des jetons de session. Si absente, une clé aléatoire est
    # générée au démarrage (les sessions sont alors perdues à chaque redémarrage).
    jwt_secret: str | None = None
    session_days: int = 7
    # À passer à true en production (HTTPS) : le cookie n'est envoyé qu'en HTTPS.
    cookie_secure: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

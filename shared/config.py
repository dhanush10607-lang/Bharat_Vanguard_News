"""
Bharat Vanguard News (BVN) — Application Configuration
Loads all settings from environment variables (.env file in development).
Uses Pydantic BaseSettings for type-safe, validated configuration.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "Bharat Vanguard News (BVN)"
    app_env: str = "development"
    app_version: str = "0.1.0"
    debug: bool = False
    secret_key: str = "change-me"
    allowed_origins: str = "http://localhost:3000"

    # --- Database (Supabase PostgreSQL) ---
    database_url: str = ""
    database_url_sync: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    # --- Redis (Upstash) ---
    redis_url: str = "redis://localhost:6379"

    # --- News APIs ---
    guardian_api_key: str = ""
    currents_api_key: str = ""
    nyt_api_key: str = ""
    hn_api_base: str = "https://hacker-news.firebaseio.com/v0"

    # --- Elasticsearch ---
    elasticsearch_url: str = ""
    elasticsearch_enabled: bool = False

    # --- NLP Models ---
    hf_cache_dir: str = "./huggingface_cache"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    summarization_model: str = "facebook/bart-large-cnn"
    topic_model: str = "facebook/bart-large-mnli"
    spacy_model: str = "en_core_web_sm"
    duplicate_threshold: float = 0.82

    # --- Collector ---
    collector_interval_minutes: int = 10
    parser_timeout_seconds: int = 30
    max_articles_per_run: int = 100
    request_delay_seconds: float = 2.0

    # --- Auth ---
    jwt_secret: str = "change-me-jwt"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080  # 7 days

    # --- Google OAuth (via Supabase Auth) ---
    google_client_id: str = ""
    google_client_secret: str = ""
    supabase_jwt_secret: str = ""      # From Supabase → Settings → API → JWT Secret
    oauth_redirect_url: str = "http://localhost:3000/auth/callback"

    # --- Frontend ---
    next_public_api_url: str = "http://localhost:8000"

    # --- Monitoring ---
    sentry_dsn: str = ""
    log_level: str = "INFO"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @model_validator(mode="after")
    def populate_database_url_sync(self) -> "Settings":
        if self.database_url and not self.database_url_sync:
            # Convert asyncpg URL to synchronous URL for Alembic
            self.database_url_sync = self.database_url.replace("+asyncpg", "")
            if self.database_url_sync.startswith("postgres://"):
                self.database_url_sync = self.database_url_sync.replace("postgres://", "postgresql://", 1)
        return self


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — call this everywhere."""
    return Settings()


settings = get_settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://signal:signal@localhost:5432/signal"
    database_url_sync: str = "postgresql://signal:signal@localhost:5432/signal"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Claude API
    anthropic_api_key: str = ""

    # Embeddings
    cohere_api_key: str = ""

    # Object Storage
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "signal-media"

    # Meilisearch
    meili_url: str = "http://localhost:7700"
    meili_master_key: str = "signal-search-key"

    # App
    app_env: str = "development"
    app_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

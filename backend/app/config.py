from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://albertsons:changeme@postgres:5432/simulations"
    sync_database_url: str = "postgresql://albertsons:changeme@postgres:5432/simulations"

    # Redis
    redis_password: str = "changeme"
    redis_url: str = "redis://:changeme@redis:6379/0"

    # Celery
    celery_broker_url: str = "redis://:changeme@redis:6379/0"
    celery_result_backend: str = "redis://:changeme@redis:6379/1"

    # Gemini
    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # App
    secret_key: str = "change_me_32_chars_minimum"
    environment: str = "development"
    log_level: str = "INFO"


settings = Settings()

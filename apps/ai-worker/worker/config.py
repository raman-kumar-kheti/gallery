import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve absolute paths relative to this config file
ROOT_DIR = pathlib.Path(__file__).resolve().parents[3]
PROJECT_DIR = pathlib.Path(__file__).resolve().parents[1]


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env", PROJECT_DIR / ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database (sync for Celery)
    database_url: str = "postgresql+psycopg2://gallery:gallery@localhost:5432/gallery"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # FAISS
    faiss_index_dir: str = "./indexes"

    # Storage (Cloudflare R2)
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "gallery-uploads"
    r2_public_url: str = ""

    # InsightFace model name
    insightface_model: str = "buffalo_l"


settings = WorkerSettings()

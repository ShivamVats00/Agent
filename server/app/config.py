"""Application configuration — loads from .env file."""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    openweathermap_api_key: str = ""
    news_api_key: str = ""

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    db_path: str = str(Path(__file__).parent.parent / "data" / "app.db")
    checkpoint_db_path: str = str(
        Path(__file__).parent.parent / "data" / "checkpoints.db"
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

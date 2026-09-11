"""Application configuration via environment variables."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Image Authenticity Detection System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    MODEL_PATH: Path = BASE_DIR / "models" / "image_detector.pt"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./forensics.db"

    # File limits
    MAX_FILE_SIZE_MB: int = 20  # 20 MB
    ALLOWED_MIME_TYPES: list = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/tiff",
    ]
    ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"]

    # Evidence fusion thresholds
    AI_CONFIDENCE_THRESHOLD_HIGH: float = 0.80  # >= this → Likely AI-Generated
    AI_CONFIDENCE_THRESHOLD_LOW: float = 0.20   # <= this → Likely Real
    # Between LOW and HIGH → Inconclusive

    # API Keys (from environment — never hardcoded)
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

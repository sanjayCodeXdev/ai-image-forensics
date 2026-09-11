"""Application configuration via environment variables."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


# Detect cloud environment (Render sets RENDER=true)
_ON_CLOUD = os.environ.get("RENDER") == "true" or os.environ.get("CLOUD_ENV") == "true"

# On cloud, use /tmp (ephemeral but process-persistent); locally use relative paths
_TMP = Path("/tmp") if _ON_CLOUD else Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Image Authenticity Detection System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = _TMP / "uploads"
    REPORTS_DIR: Path = _TMP / "reports"
    MODEL_PATH: Path = BASE_DIR / "models" / "image_detector.pt"

    # Database — use /tmp on cloud so SQLite can write
    DATABASE_URL: str = (
        f"sqlite+aiosqlite:////tmp/forensics.db"
        if _ON_CLOUD
        else "sqlite+aiosqlite:///./forensics.db"
    )

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

    # CORS — base list + extras from ALLOWED_ORIGINS env var (comma-separated)
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        # GitHub Pages
        "https://sanjayCodeXdev.github.io",
        "https://sanjayCodeXdev.github.io/ai-image-forensics",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def get_all_origins(self) -> list:
        """Merge base origins with any extra ones set via ALLOWED_ORIGINS env var."""
        extra = os.environ.get("ALLOWED_ORIGINS", "")
        extras = [o.strip() for o in extra.split(",") if o.strip()]
        return list(set(self.CORS_ORIGINS + extras))


settings = Settings()

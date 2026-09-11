"""Health check route."""
from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas import HealthResponse
from app.config import settings

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc),
    )

"""
FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload --port 8000
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routes.health_routes import router as health_router
from app.routes.analysis_routes import router as analysis_router
from app.routes.history_routes import router as history_router

# On cloud deployments, allow all origins so any frontend can connect.
# Locally, restrict to the configured whitelist.
_ON_CLOUD = os.environ.get("RENDER") == "true"
_CORS_ORIGINS = ["*"] if _ON_CLOUD else settings.get_all_origins()
_ALLOW_CREDENTIALS = not _ON_CLOUD  # credentials not allowed with wildcard origins


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    settings.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    await init_db()
    yield
    # Shutdown — nothing special needed


# ── App factory ────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI Image Authenticity Detection and Digital Forensics System. "
        "Analyses uploaded images using metadata extraction, provenance checking, "
        "AI visual detection, and digital forensics to estimate whether an image "
        "is real or AI-generated. Results are estimations, not definitive proof."
    ),
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(history_router)


# ── Root redirect ─────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": f"{settings.APP_NAME} is running.",
        "docs": "/api/docs",
        "health": "/api/health",
    }

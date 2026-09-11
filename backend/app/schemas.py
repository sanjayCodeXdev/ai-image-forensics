"""Pydantic schemas for request / response validation."""
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict


# ── Health ────────────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


# ── Analysis ──────────────────────────────────────────────────────────────────
class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: str
    original_filename: str
    file_size: int
    file_type: str
    image_width: Optional[int]
    image_height: Optional[int]
    final_result: Optional[str]
    confidence_score: Optional[float]
    ai_probability: Optional[float]
    real_probability: Optional[float]
    metadata_status: Optional[str]
    provenance_status: Optional[str]
    watermark_status: Optional[str]
    forensic_score: Optional[float]
    model_name: Optional[str]
    model_version: Optional[str]
    created_at: datetime


class AnalysisDetailResponse(AnalysisResponse):
    """Full response including nested JSON results."""
    analysis_json: Optional[str]


# ── History ───────────────────────────────────────────────────────────────────
class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: str
    original_filename: str
    file_size: int
    file_type: str
    final_result: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime


class HistoryResponse(BaseModel):
    total: int
    items: List[HistoryItem]


# ── Error ─────────────────────────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

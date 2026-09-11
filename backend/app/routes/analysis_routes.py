"""
Analysis routes — POST /api/analyze and GET endpoints for results/report/image.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path


class _SafeEncoder(json.JSONEncoder):
    """Fallback encoder: converts bytes → hex string, Path → str, others → str."""
    def default(self, obj):
        if isinstance(obj, bytes):
            try:
                return obj.decode("utf-8", errors="replace")
            except Exception:
                return obj.hex()
        if isinstance(obj, Path):
            return str(obj)
        return str(obj)

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models import Analysis
from app.schemas import AnalysisResponse, AnalysisDetailResponse
from app.utils.security_utils import is_safe_path

# Services
from app.services.upload_service import validate_and_store
from app.services.metadata_analyzer import analyze_metadata
from app.services.provenance_analyzer import analyze_provenance
from app.services.watermark_analyzer import analyze_watermark
from app.services.visual_detector import analyze_visual
from app.services.forensic_analyzer import analyze_forensics
from app.services.evidence_fusion import fuse_evidence
from app.services.report_generator import generate_report

router = APIRouter(prefix="/api", tags=["Analysis"])


# ── POST /api/analyze ─────────────────────────────────────────────────────────

@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Main analysis endpoint.
    Runs the full pipeline: upload → metadata → provenance → watermark
    → visual AI model → forensics → evidence fusion → store in DB.
    """
    # ── Step 1: Validate and store file ──────────────────────────────────────
    file_info = await validate_and_store(file)
    raw_bytes  = file_info["raw_bytes"]
    mime_type  = file_info["mime_type"]

    # ── Step 2: Metadata extraction ───────────────────────────────────────────
    metadata_result = analyze_metadata(raw_bytes, file_info["original_filename"], mime_type)

    # ── Step 3: Provenance / C2PA ─────────────────────────────────────────────
    provenance_result = analyze_provenance(raw_bytes, mime_type)

    # ── Step 4: Watermark / provider signals ──────────────────────────────────
    watermark_result = analyze_watermark(raw_bytes, mime_type)

    # ── Step 5: AI visual detection ───────────────────────────────────────────
    visual_result = analyze_visual(raw_bytes)

    # ── Step 6: Digital forensics ─────────────────────────────────────────────
    forensic_result = analyze_forensics(raw_bytes, mime_type)

    # ── Step 7: Evidence fusion ───────────────────────────────────────────────
    fusion_result = fuse_evidence(
        metadata_result, provenance_result, watermark_result,
        visual_result, forensic_result,
    )

    # ── Step 8: Build full report ─────────────────────────────────────────────
    analysis_id = str(uuid.uuid4())
    # Strip non-serialisable objects before passing to report generator
    safe_file_info = {
        k: v for k, v in file_info.items()
        if k not in ("raw_bytes", "pil_image", "stored_path")
    }
    full_report = generate_report(
        analysis_id, safe_file_info,
        metadata_result, provenance_result, watermark_result,
        visual_result, forensic_result, fusion_result,
    )

    # ── Step 9: Persist to database ───────────────────────────────────────────
    record = Analysis(
        analysis_id       = analysis_id,
        original_filename = file_info["original_filename"],
        stored_filename   = file_info["stored_filename"],
        file_size         = file_info["file_size"],
        file_type         = file_info["file_type"],
        image_width       = file_info["image_width"],
        image_height      = file_info["image_height"],
        final_result      = fusion_result.get("final_result"),
        confidence_score  = fusion_result.get("confidence_score"),
        ai_probability    = fusion_result.get("ai_probability"),
        real_probability  = fusion_result.get("real_probability"),
        metadata_status   = metadata_result.get("status"),
        provenance_status = provenance_result.get("status"),
        watermark_status  = watermark_result.get("overall_status"),
        forensic_score    = forensic_result.get("anomaly_score"),
        model_name        = visual_result.get("model_name"),
        model_version     = visual_result.get("model_version"),
        analysis_json     = json.dumps(full_report, cls=_SafeEncoder),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return AnalysisResponse.model_validate(record)


# ── GET /api/analysis/{id} ────────────────────────────────────────────────────

@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str, db: AsyncSession = Depends(get_db)):
    row = await _get_or_404(analysis_id, db)
    return AnalysisResponse.model_validate(row)


# ── GET /api/analysis/{id}/report ─────────────────────────────────────────────

@router.get("/analysis/{analysis_id}/report")
async def get_analysis_report(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """Return the full JSON analysis report."""
    row = await _get_or_404(analysis_id, db)
    if not row.analysis_json:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not available.")
    return json.loads(row.analysis_json)


# ── GET /api/analysis/{id}/image ──────────────────────────────────────────────

@router.get("/analysis/{analysis_id}/image")
async def get_analysis_image(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """Serve the stored image for display in the frontend."""
    row = await _get_or_404(analysis_id, db)
    img_path = settings.UPLOAD_DIR / row.stored_filename

    # Safety: ensure path is strictly within UPLOAD_DIR
    if not is_safe_path(settings.UPLOAD_DIR, img_path):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied.")

    if not img_path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Image file not found.")

    return FileResponse(
        path=img_path,
        media_type=_ext_to_media_type(img_path.suffix),
        filename=row.original_filename,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_or_404(analysis_id: str, db: AsyncSession) -> Analysis:
    result = await db.execute(
        select(Analysis).where(Analysis.analysis_id == analysis_id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Analysis not found.")
    return row


def _ext_to_media_type(ext: str) -> str:
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
    }.get(ext.lower(), "application/octet-stream")

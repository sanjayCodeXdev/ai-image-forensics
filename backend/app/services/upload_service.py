"""Upload service — file validation, storage, and basic image info extraction."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Dict, Any

from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.config import settings
from app.utils.file_utils import save_upload
from app.utils.image_utils import open_image_safely
from app.utils.security_utils import generate_safe_filename, sanitize_display_filename


MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # convert MB → bytes


async def validate_and_store(file: UploadFile) -> Dict[str, Any]:
    """
    Validate an uploaded file and save it to disk.
    Returns a dict with metadata needed to start analysis.
    Raises HTTPException on any validation failure.
    """
    # 1. File must not be empty
    raw = await file.read()
    if not raw:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Uploaded file is empty.")

    # 2. Size check
    if len(raw) > MAX_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File exceeds the {settings.MAX_FILE_SIZE_MB} MB limit.",
        )

    # 3. Extension check
    original_name = sanitize_display_filename(file.filename or "upload")
    suffix = Path(original_name).suffix.lower()
    if suffix not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported file type '{suffix}'. "
            f"Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    # 4. MIME type sniffing (actual bytes, not just the declared Content-Type)
    try:
        detected_mime = _sniff_mime(raw)
    except Exception:
        detected_mime = file.content_type or ""

    if detected_mime not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"File content does not match an allowed image type. "
            f"Detected: '{detected_mime}'.",
        )

    # 5. Image integrity check — try to fully decode the image
    img = open_image_safely(raw)
    if img is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "The uploaded file is corrupted or cannot be decoded as an image.",
        )

    # 6. Generate a safe stored filename and persist to disk
    stored_name = generate_safe_filename(original_name)
    dest_path = settings.UPLOAD_DIR / stored_name
    await save_upload(raw, dest_path)

    width, height = img.size

    return {
        "original_filename": original_name,
        "stored_filename": stored_name,
        "stored_path": dest_path,
        "raw_bytes": raw,
        "file_size": len(raw),
        "mime_type": detected_mime,
        "file_type": suffix.lstrip(".").upper(),
        "image_width": width,
        "image_height": height,
        "pil_image": img,
    }


# ── MIME sniffing ─────────────────────────────────────────────────────────────

def _sniff_mime(data: bytes) -> str:
    """
    Detect MIME type from file magic bytes.
    Falls back to a manual check if python-magic is not available.
    """
    try:
        import magic as libmagic
        return libmagic.from_buffer(data, mime=True)
    except (ImportError, Exception):
        return _manual_sniff(data)


def _manual_sniff(data: bytes) -> str:
    """Minimal magic-byte MIME detection without external deps."""
    sig = data[:12]
    if sig[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if sig[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if sig[:4] in (b"RIFF",) and data[8:12] == b"WEBP":
        return "image/webp"
    if sig[:4] in (b"II*\x00", b"MM\x00*"):
        return "image/tiff"
    # Let Pillow decide
    try:
        img = Image.open(BytesIO(data))
        mime_map = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "WEBP": "image/webp",
            "TIFF": "image/tiff",
        }
        return mime_map.get(img.format or "", "application/octet-stream")
    except Exception:
        return "application/octet-stream"

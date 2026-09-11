"""
Metadata Analyzer — extracts EXIF, XMP, IPTC and PNG metadata from images.

IMPORTANT PRINCIPLE:
  Metadata is supporting evidence only.  It can be removed, modified, or
  falsified.  Missing metadata does NOT mean an image is AI-generated, and
  camera metadata does NOT automatically prove an image is real.
"""
from __future__ import annotations

import struct
from io import BytesIO
from typing import Any, Dict, List, Optional

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_metadata(raw_bytes: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
    """
    Extract all available metadata from image bytes and return a structured
    analysis result with a classification and limitations notice.
    """
    img = Image.open(BytesIO(raw_bytes))
    fmt = (img.format or "").upper()

    exif_data = _extract_exif(img)
    xmp_data  = _extract_xmp(raw_bytes)
    iptc_data = _extract_iptc(img)
    png_data  = _extract_png_metadata(img, fmt)

    findings  = _classify_findings(exif_data, xmp_data, iptc_data, png_data)
    status    = _determine_status(findings)
    score     = _compute_score(findings)          # 0 = strongly AI signals, 1 = strongly real signals

    return {
        "status": status,
        "score": score,
        "findings": findings,
        "exif": exif_data,
        "xmp": xmp_data,
        "iptc": iptc_data,
        "png_metadata": png_data,
        "summary": _build_summary(status, findings),
        "limitations": (
            "⚠ Metadata is supporting evidence only. "
            "It can be removed, modified, or falsified. "
            "Missing metadata does NOT prove an image is AI-generated. "
            "Camera metadata does NOT automatically prove an image is real."
        ),
    }


# ── EXIF extraction ────────────────────────────────────────────────────────────

def _extract_exif(img: Image.Image) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    try:
        raw_exif = img._getexif()   # type: ignore[attr-defined]
        if not raw_exif:
            return result
        for tag_id, value in raw_exif.items():
            tag = TAGS.get(tag_id, str(tag_id))
            if tag == "GPSInfo" and isinstance(value, dict):
                result["GPSInfo"] = {
                    GPSTAGS.get(k, str(k)): v for k, v in value.items()
                }
            else:
                result[tag] = _safe_value(value)
    except (AttributeError, struct.error, Exception):
        pass
    return result


# ── XMP extraction ─────────────────────────────────────────────────────────────

def _extract_xmp(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Naive XMP extraction: locate the XMP packet in raw bytes and return
    a dict of key fields without pulling in an XML parser dependency.
    """
    try:
        start = raw_bytes.find(b"<x:xmpmeta")
        if start == -1:
            start = raw_bytes.find(b"<?xpacket")
        if start == -1:
            return {}
        end = raw_bytes.find(b"</x:xmpmeta>")
        if end == -1:
            end = raw_bytes.find(b"<?xpacket end")
        chunk = raw_bytes[start : end + 50].decode("utf-8", errors="replace")
        fields: Dict[str, Any] = {"raw_present": True, "snippet": chunk[:500]}
        # Extract common XMP fields via simple string search
        for key in ("xmp:CreatorTool", "xmp:CreateDate", "xmp:ModifyDate",
                    "dc:creator", "photoshop:Credit", "Iptc4xmpCore:Source"):
            tag_open  = f"<{key}>"
            tag_close = f"</{key}>"
            if tag_open in chunk:
                s = chunk.index(tag_open) + len(tag_open)
                e = chunk.index(tag_close, s)
                fields[key] = chunk[s:e].strip()
        return fields
    except Exception:
        return {}


# ── IPTC extraction ────────────────────────────────────────────────────────────

def _extract_iptc(img: Image.Image) -> Dict[str, Any]:
    try:
        from PIL import IptcImagePlugin
        iptc = IptcImagePlugin.getiptcinfo(img)
        if not iptc:
            return {}
        result: Dict[str, Any] = {}
        iptc_tags = {
            (2, 5):  "ObjectName",
            (2, 10): "Urgency",
            (2, 25): "Keywords",
            (2, 55): "DateCreated",
            (2, 60): "TimeCreated",
            (2, 80): "Creator",
            (2, 85): "AuthorTitle",
            (2, 90): "City",
            (2, 101): "CountryName",
            (2, 105): "Headline",
            (2, 110): "Credit",
            (2, 115): "Source",
            (2, 120): "Caption",
        }
        for k, v in iptc.items():
            label = iptc_tags.get(k, str(k))
            result[label] = v.decode("utf-8", errors="replace") if isinstance(v, bytes) else str(v)
        return result
    except Exception:
        return {}


# ── PNG text metadata ──────────────────────────────────────────────────────────

def _extract_png_metadata(img: Image.Image, fmt: str) -> Dict[str, Any]:
    if fmt != "PNG":
        return {}
    try:
        return {k: str(v) for k, v in (img.info or {}).items()
                if k not in ("exif", "icc_profile")}
    except Exception:
        return {}


# ── Classification logic ───────────────────────────────────────────────────────

# Known AI generator software strings (case-insensitive substrings)
_AI_SOFTWARE_HINTS = [
    "stable diffusion", "midjourney", "dall-e", "dalle", "firefly",
    "nightcafe", "dream", "automatic1111", "invoke ai", "comfyui",
    "novelai", "bing image creator", "adobe firefly", "imagen",
    "ideogram", "leonardo", "runway", "pika",
]

# Known editing software
_EDIT_SOFTWARE_HINTS = [
    "photoshop", "lightroom", "gimp", "affinity", "capture one",
    "luminar", "darktable",
]


def _classify_findings(
    exif: Dict, xmp: Dict, iptc: Dict, png: Dict
) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []

    if not exif and not xmp and not iptc:
        findings.append({
            "type": "metadata_missing",
            "label": "No EXIF / XMP / IPTC metadata found",
            "weight": "neutral",
        })
    else:
        findings.append({
            "type": "metadata_found",
            "label": "Metadata is present",
            "weight": "positive",
        })

    # Camera info
    make  = exif.get("Make", "")
    model = exif.get("Model", "")
    if make or model:
        findings.append({
            "type": "camera_info",
            "label": f"Camera info: {make} {model}".strip(),
            "weight": "positive",
        })

    # Software field
    software = str(exif.get("Software", "")
                   or xmp.get("xmp:CreatorTool", "")
                   or png.get("Software", ""))

    if software:
        lower = software.lower()
        if any(hint in lower for hint in _AI_SOFTWARE_HINTS):
            findings.append({
                "type": "ai_software_detected",
                "label": f"Software field indicates possible AI tool: '{software}'",
                "weight": "negative",
            })
        elif any(hint in lower for hint in _EDIT_SOFTWARE_HINTS):
            findings.append({
                "type": "editing_software",
                "label": f"Editing software detected: '{software}'",
                "weight": "neutral",
            })
        else:
            findings.append({
                "type": "software_found",
                "label": f"Software: '{software}'",
                "weight": "neutral",
            })

    # Date info
    date = exif.get("DateTimeOriginal") or exif.get("DateTime") or xmp.get("xmp:CreateDate")
    if date:
        findings.append({
            "type": "date_info",
            "label": f"Date/time recorded: {date}",
            "weight": "positive",
        })

    # GPS
    if "GPSInfo" in exif:
        findings.append({
            "type": "gps_info",
            "label": "GPS coordinates embedded",
            "weight": "positive",
        })

    return findings


def _determine_status(findings: List[Dict]) -> str:
    types = {f["type"] for f in findings}
    if "ai_software_detected" in types:
        return "metadata_indicates_possible_ai_software"
    if "metadata_missing" in types:
        return "metadata_missing"
    if "camera_info" in types:
        return "metadata_found"
    if "metadata_found" in types:
        return "metadata_found"
    return "inconclusive"


def _compute_score(findings: List[Dict]) -> float:
    """
    Returns a score in [0, 1].
    1.0 = strong real-image signals in metadata.
    0.0 = strong AI-generation signals in metadata.
    Values near 0.5 = inconclusive.
    """
    weights = {"positive": +1, "negative": -1, "neutral": 0}
    total = sum(weights.get(f.get("weight", "neutral"), 0) for f in findings)
    # Normalise to [0, 1]; clamp
    normalised = 0.5 + total * 0.1
    return round(max(0.0, min(1.0, normalised)), 3)


def _build_summary(status: str, findings: List[Dict]) -> str:
    labels = [f["label"] for f in findings]
    base   = "; ".join(labels) if labels else "No metadata available."
    notice = (
        "Note: Metadata alone is not proof of authenticity or AI generation. "
        "It can be stripped, edited, or fabricated."
    )
    return f"{base}. {notice}"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _safe_value(v: Any) -> Any:
    """Convert non-serialisable EXIF values to strings."""
    if isinstance(v, (str, int, float, bool, type(None))):
        return v
    if isinstance(v, bytes):
        try:
            return v.decode("utf-8", errors="replace")
        except Exception:
            return v.hex()
    if isinstance(v, dict):
        return {str(k): _safe_value(val) for k, val in v.items()}
    if isinstance(v, (list, tuple)):
        return [_safe_value(x) for x in v]
    return str(v)

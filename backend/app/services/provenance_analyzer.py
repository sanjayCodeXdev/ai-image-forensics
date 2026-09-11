"""
Provenance Analyzer — checks for C2PA manifests and Content Credentials.

IMPORTANT:
  Absence of C2PA credentials does NOT prove an image is fake.
  C2PA information may be removed through screenshots, compression, editing,
  or re-uploading.  This service does not generate fake verification results.
"""
from __future__ import annotations

from typing import Any, Dict


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_provenance(raw_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    """
    Attempt to detect C2PA / Content Credentials in the raw image bytes.
    Returns a structured result with a transparent status.
    """
    manifest = _find_c2pa_manifest(raw_bytes)

    if manifest is not None:
        status  = "credentials_found_unverified"
        details = manifest
        summary = (
            "A C2PA-style manifest was found in the image. "
            "Full cryptographic verification requires the c2pa-python library "
            "which is not currently installed. The manifest content is shown below."
        )
    else:
        status  = "no_credentials_found"
        details = {}
        summary = (
            "No C2PA / Content Credentials manifest was detected. "
            "This is normal — the majority of images do not carry C2PA data. "
            "Absence of credentials does NOT indicate the image is fake."
        )

    return {
        "status": status,
        "details": details,
        "summary": summary,
        "limitations": (
            "C2PA verification requires a trusted certificate chain. "
            "Even verified credentials can be bypassed via screenshot or re-export. "
            "Absence of credentials does NOT prove an image is AI-generated. "
            "Full cryptographic verification is unavailable in this deployment "
            "(install the c2pa-python package to enable it)."
        ),
    }


# ── Detection helpers ─────────────────────────────────────────────────────────

# C2PA uses a UUID-based box in JPEG/MP4 or an XMP packet.
_C2PA_JUMBF_UUID = b"\x6a\x50\x20\x20"   # rough marker in JPEG streams
_C2PA_XMP_TAG   = b"c2pa"
_C2PA_CR_TAG    = b"ContentCredentials"


def _find_c2pa_manifest(data: bytes) -> Dict[str, Any] | None:
    """
    Scan raw bytes for C2PA / Content Credentials markers.
    Returns a dict with detected fields, or None if not found.
    """
    lower_chunk = data[:4096].lower()

    found_xmp  = _C2PA_XMP_TAG in lower_chunk
    found_cr   = _C2PA_CR_TAG in data[:8192]

    if not (found_xmp or found_cr):
        return None

    # Try to extract a snippet for display
    snippet = _extract_snippet(data, _C2PA_CR_TAG)
    return {
        "c2pa_marker_found": True,
        "content_credentials_marker": found_cr,
        "xmp_c2pa_marker": found_xmp,
        "raw_snippet": snippet,
        "verification_status": "unverified",
        "note": (
            "Marker detected but cryptographic signature was not verified. "
            "Install 'c2pa-python' for full verification support."
        ),
    }


def _extract_snippet(data: bytes, marker: bytes) -> str:
    pos = data.find(marker)
    if pos == -1:
        return ""
    chunk = data[max(0, pos - 20): pos + 200]
    return chunk.decode("utf-8", errors="replace")

"""
Watermark / Provider Signal Analyzer.

Checks for AI-provider-specific provenance signals where officially supported.
API keys are read from environment variables — never hardcoded.

IMPORTANT:
  "Signal not detected" must NEVER be interpreted as proof that the image is real.
  If an API key is not configured, the status is clearly "verification_unavailable".
"""
import os
from typing import Any, Dict, List

from app.config import settings


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_watermark(raw_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    """
    Attempt provider-specific AI watermark / provenance signal checks.
    Returns structured results with honest availability status.
    """
    results: Dict[str, Any] = {
        "providers_checked": [],
        "overall_status": "verification_unavailable",
        "signal_detected": False,
        "summary": "",
        "limitations": (
            "'Signal not detected' does NOT prove the image is real. "
            "Many AI systems do not embed detectable watermarks. "
            "Watermarks can be removed by cropping, compression, or re-generation. "
            "Provider verification APIs may not be publicly available."
        ),
    }

    provider_results: List[Dict[str, Any]] = []

    # ── OpenAI provenance signal ──────────────────────────────────────────────
    openai_result = _check_openai_signal(raw_bytes)
    provider_results.append(openai_result)

    # ── Google SynthID (placeholder — public API not yet available) ───────────
    google_result = _check_google_synthid(raw_bytes)
    provider_results.append(google_result)

    results["providers_checked"] = provider_results

    # Derive overall status
    statuses = [r["status"] for r in provider_results]
    if "signal_detected" in statuses:
        results["overall_status"] = "signal_detected"
        results["signal_detected"] = True
    elif all(s == "verification_unavailable" for s in statuses):
        results["overall_status"] = "verification_unavailable"
    elif "signal_not_detected" in statuses:
        results["overall_status"] = "signal_not_detected"
    else:
        results["overall_status"] = "inconclusive"

    results["summary"] = _build_summary(provider_results)
    return results


# ── Provider checks ───────────────────────────────────────────────────────────

def _check_openai_signal(raw_bytes: bytes) -> Dict[str, Any]:
    """
    OpenAI does not currently expose a public image provenance verification API.
    This stub returns an honest 'unavailable' status.
    """
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return {
            "provider": "OpenAI",
            "status": "verification_unavailable",
            "reason": "OPENAI_API_KEY not configured.",
            "note": "OpenAI does not currently offer a public image verification API.",
        }

    # Future: call OpenAI's provenance endpoint when/if available
    return {
        "provider": "OpenAI",
        "status": "verification_unavailable",
        "reason": "OpenAI does not currently provide a public image provenance API.",
        "note": "API key is configured but verification endpoint is not publicly available.",
    }


def _check_google_synthid(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Google SynthID watermark verification is not available as a public API.
    This stub returns an honest 'unavailable' status.
    """
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        return {
            "provider": "Google SynthID",
            "status": "verification_unavailable",
            "reason": "GOOGLE_API_KEY not configured.",
            "note": (
                "Google SynthID verification is not publicly available as an API. "
                "It is used internally by Google's own products."
            ),
        }

    return {
        "provider": "Google SynthID",
        "status": "verification_unavailable",
        "reason": "SynthID verification API is not publicly available.",
        "note": "API key is configured but SynthID verification is not a public endpoint.",
    }


def _build_summary(providers: List[Dict[str, Any]]) -> str:
    lines = []
    for p in providers:
        status = p.get("status", "unknown")
        name   = p.get("provider", "Unknown")
        reason = p.get("reason", "")
        lines.append(f"{name}: {status.replace('_', ' ').title()}. {reason}")
    return " | ".join(lines)

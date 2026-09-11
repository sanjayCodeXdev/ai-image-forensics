"""
Evidence Fusion — combines all sub-analysis results into a final verdict.

Weighting system (transparent):
  - Visual AI Model:   40%  (highest weight — direct classifier)
  - Forensic Analysis: 30%  (strong supporting signal)
  - Metadata:          15%  (weak — easily falsified)
  - Provenance:        10%  (strong if verified, neutral if absent)
  - Watermark:          5%  (rarely available)

Thresholds (configurable via config.py):
  ai_probability >= HIGH_THRESHOLD → "likely_ai_generated"
  ai_probability <= LOW_THRESHOLD  → "likely_real"
  otherwise                        → "inconclusive"

IMPORTANT: The final report always includes a disclaimer that this
estimation should not be considered definitive proof.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.config import settings


# ── Weights ────────────────────────────────────────────────────────────────────
WEIGHTS = {
    "visual_model":  0.40,
    "forensic":      0.30,
    "metadata":      0.15,
    "provenance":    0.10,
    "watermark":     0.05,
}


# ── Public API ────────────────────────────────────────────────────────────────

def fuse_evidence(
    metadata_result: Dict[str, Any],
    provenance_result: Dict[str, Any],
    watermark_result: Dict[str, Any],
    visual_result: Dict[str, Any],
    forensic_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Fuse sub-analysis results into a final classification and confidence score.
    Returns a structured dict with full transparency.
    """
    contributions: Dict[str, Optional[float]] = {}

    # ── Visual model ──────────────────────────────────────────────────────────
    vm_ai_prob: Optional[float] = visual_result.get("ai_probability")
    if vm_ai_prob is not None and visual_result.get("status") == "success":
        contributions["visual_model"] = vm_ai_prob
    else:
        contributions["visual_model"] = None   # unavailable

    # ── Forensic analysis ─────────────────────────────────────────────────────
    forensic_score = forensic_result.get("anomaly_score")
    if forensic_score is not None:
        contributions["forensic"] = float(forensic_score)
    else:
        contributions["forensic"] = None

    # ── Metadata ──────────────────────────────────────────────────────────────
    meta_score = metadata_result.get("score")
    if meta_score is not None:
        # metadata score: 1 = strong real signals, 0 = strong AI signals
        # invert so higher = more AI evidence
        contributions["metadata"] = 1.0 - float(meta_score)
    else:
        contributions["metadata"] = None

    # ── Provenance ────────────────────────────────────────────────────────────
    prov_status = provenance_result.get("status", "")
    contributions["provenance"] = _provenance_to_ai_prob(prov_status)

    # ── Watermark ─────────────────────────────────────────────────────────────
    wm_status = watermark_result.get("overall_status", "")
    contributions["watermark"] = _watermark_to_ai_prob(wm_status)

    # ── Weighted fusion ────────────────────────────────────────────────────────
    ai_probability, weights_used = _weighted_average(contributions)

    # ── Classification ────────────────────────────────────────────────────────
    classification = _classify(ai_probability)
    real_probability = round(1.0 - ai_probability, 4)

    # ── Evidence summary ──────────────────────────────────────────────────────
    positive, negative = _collect_evidence(
        metadata_result, provenance_result, watermark_result,
        visual_result, forensic_result, contributions
    )

    return {
        "final_result":       classification,
        "ai_probability":     round(ai_probability, 4),
        "real_probability":   real_probability,
        "confidence_score":   round(_to_confidence(ai_probability, classification), 4),
        "contributions":      {k: round(v, 4) if v is not None else None
                               for k, v in contributions.items()},
        "weights_used":       weights_used,
        "positive_indicators": positive,
        "negative_indicators": negative,
        "thresholds": {
            "likely_ai":   settings.AI_CONFIDENCE_THRESHOLD_HIGH,
            "likely_real": settings.AI_CONFIDENCE_THRESHOLD_LOW,
        },
        "summary": _build_summary(classification, ai_probability),
        "disclaimer": (
            "This result is an estimation based on available technical evidence. "
            "It should not be considered definitive proof of AI generation or "
            "authenticity.  Multiple factors, including image processing, "
            "compression, and editing, can influence the scores."
        ),
    }


# ── Internal helpers ──────────────────────────────────────────────────────────

def _weighted_average(
    contributions: Dict[str, Optional[float]]
) -> Tuple[float, Dict[str, float]]:
    """Compute weighted average, ignoring None values and re-normalising weights."""
    total_w = 0.0
    total_s = 0.0
    weights_used: Dict[str, float] = {}

    for key, score in contributions.items():
        w = WEIGHTS.get(key, 0)
        if score is not None:
            total_s += score * w
            total_w += w
            weights_used[key] = round(w, 3)

    if total_w == 0:
        return 0.5, {}   # no data — neutral

    return total_s / total_w, weights_used


def _classify(ai_prob: float) -> str:
    if ai_prob >= settings.AI_CONFIDENCE_THRESHOLD_HIGH:
        return "likely_ai_generated"
    if ai_prob <= settings.AI_CONFIDENCE_THRESHOLD_LOW:
        return "likely_real"
    return "inconclusive"


def _to_confidence(ai_prob: float, classification: str) -> float:
    """
    Convert ai_probability to a confidence % (distance from 0.5).
    Returns a value in [0, 1].
    """
    return abs(ai_prob - 0.5) * 2


def _provenance_to_ai_prob(status: str) -> float:
    """
    Map provenance status to an AI-probability contribution.
    Absence of provenance → neutral (0.5), not evidence of AI.
    """
    mapping = {
        "verified_provenance_found": 0.10,   # strong real signal
        "valid_credentials_found":   0.15,
        "credentials_found_unverified": 0.40,
        "no_credentials_found":      0.50,   # neutral
        "verification_unavailable":  0.50,
        "unsupported_file":          0.50,
    }
    return mapping.get(status, 0.50)


def _watermark_to_ai_prob(status: str) -> float:
    """
    Map watermark status to an AI-probability contribution.
    "Not detected" → neutral, NOT real.
    """
    mapping = {
        "signal_detected":           0.90,   # strong AI signal
        "signal_not_detected":       0.50,   # neutral — cannot conclude real
        "verification_unavailable":  0.50,
        "inconclusive":              0.50,
    }
    return mapping.get(status, 0.50)


def _collect_evidence(
    meta: Dict, prov: Dict, wm: Dict,
    visual: Dict, forensic: Dict,
    contributions: Dict
) -> Tuple[List[str], List[str]]:
    """Collect human-readable positive/negative evidence points."""
    positive: List[str] = []   # points suggesting real image
    negative: List[str] = []   # points suggesting AI generation

    # Metadata
    mstatus = meta.get("status", "")
    if mstatus == "metadata_found":
        positive.append("Camera metadata found (EXIF).")
    if mstatus == "metadata_indicates_possible_ai_software":
        negative.append("Metadata references a possible AI software tool.")

    # Provenance
    pstatus = prov.get("status", "")
    if "verified" in pstatus:
        positive.append("C2PA / Content Credentials detected.")
    if pstatus == "no_credentials_found":
        positive.append("No C2PA credentials found (neutral — most images lack them).")

    # Visual model
    if visual.get("status") == "success":
        ai_p = visual.get("ai_probability", 0.5)
        if ai_p is not None:
            if ai_p >= 0.70:
                negative.append(f"AI visual model: {ai_p*100:.1f}% AI probability.")
            elif ai_p <= 0.30:
                positive.append(f"AI visual model: {(1-ai_p)*100:.1f}% real probability.")
            else:
                negative.append(f"AI visual model result is inconclusive ({ai_p*100:.1f}% AI).")
    elif visual.get("status") == "model_not_configured":
        negative.append("AI visual model not configured — this component was excluded.")

    # Forensics
    fscore = forensic.get("anomaly_score")
    if fscore is not None:
        if fscore > 0.60:
            negative.append(f"Forensic analysis detected anomalies (score: {fscore:.2f}).")
        elif fscore < 0.35:
            positive.append(f"Forensic analysis shows few anomalies (score: {fscore:.2f}).")
        else:
            positive.append(f"Forensic analysis is inconclusive (score: {fscore:.2f}).")

    return positive, negative


def _build_summary(classification: str, ai_prob: float) -> str:
    label_map = {
        "likely_ai_generated": "Likely AI-Generated",
        "likely_real":         "Likely Real / Authentic",
        "inconclusive":        "Inconclusive",
    }
    label = label_map.get(classification, classification)
    return (
        f"Classification: {label} "
        f"(AI probability: {ai_prob*100:.1f}%). "
        "This estimation is based on a weighted combination of metadata analysis, "
        "provenance checking, visual AI detection, and digital forensics."
    )

"""
Digital Image Forensics Analyzer.

Uses OpenCV + NumPy to compute multiple supporting forensic signals.
These signals are evidence, not absolute proof.

Signals computed:
  - JPEG compression / Error Level Analysis (ELA) score
  - Noise consistency across image regions
  - Frequency-domain anomaly (DCT analysis)
  - Texture anomaly (Local Binary Patterns proxy)
  - Edge consistency
  - Color distribution analysis
  - Overall forensic anomaly score
"""
from __future__ import annotations

import logging
import math
import tempfile
import os
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_forensics(raw_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    """
    Run all forensic sub-analyses and return a structured result.
    """
    try:
        import cv2
    except ImportError:
        return _cv2_unavailable()

    img_pil = Image.open(BytesIO(raw_bytes)).convert("RGB")
    img_np  = np.array(img_pil)                          # H×W×3, uint8
    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)  # H×W

    results: Dict[str, Any] = {}

    # ── 1. ELA / JPEG compression score ──────────────────────────────────────
    results["ela"] = _compute_ela(raw_bytes, img_pil, mime_type)

    # ── 2. Noise consistency ──────────────────────────────────────────────────
    results["noise_consistency"] = _compute_noise_consistency(img_gray)

    # ── 3. Frequency-domain (DCT) analysis ────────────────────────────────────
    results["frequency_anomaly"] = _compute_frequency_anomaly(img_gray)

    # ── 4. Texture anomaly ────────────────────────────────────────────────────
    results["texture_anomaly"] = _compute_texture_anomaly(img_gray)

    # ── 5. Edge consistency ────────────────────────────────────────────────────
    results["edge_consistency"] = _compute_edge_consistency(img_gray, cv2)

    # ── 6. Color distribution ─────────────────────────────────────────────────
    results["color_distribution"] = _compute_color_distribution(img_np)

    # ── 7. Aggregate forensic score ───────────────────────────────────────────
    anomaly_score = _aggregate_anomaly(results)
    results["anomaly_score"] = anomaly_score

    summary = _build_summary(anomaly_score, results)

    return {
        "status": "completed",
        "anomaly_score": round(anomaly_score, 4),
        "details": results,
        "summary": summary,
        "chart_data": _build_chart_data(results),
        "limitations": (
            "Forensic analysis detects statistical anomalies that may be associated "
            "with AI generation, but these signals also appear in heavily compressed, "
            "edited, or resized photographs.  This is supporting evidence, not proof."
        ),
    }


# ── Sub-analyses ──────────────────────────────────────────────────────────────

def _compute_ela(raw_bytes: bytes, img_pil: Image.Image, mime_type: str) -> Dict[str, Any]:
    """
    Error Level Analysis: re-save at known quality, diff against original.
    Higher mean ELA → more likely re-saved or composited.
    """
    try:
        buf = BytesIO()
        rgb = img_pil.convert("RGB")
        rgb.save(buf, format="JPEG", quality=75)
        buf.seek(0)
        recompressed = Image.open(buf).convert("RGB")

        orig_arr  = np.array(rgb,          dtype=np.float32)
        comp_arr  = np.array(recompressed, dtype=np.float32)
        diff      = np.abs(orig_arr - comp_arr)
        mean_ela  = float(np.mean(diff))
        max_ela   = float(np.max(diff))

        # Normalise to [0,1] — typical JPEG originals < 8, composites > 20
        score = min(mean_ela / 25.0, 1.0)

        return {
            "score": round(score, 4),
            "mean_diff": round(mean_ela, 3),
            "max_diff":  round(max_ela, 3),
            "interpretation": (
                "High ELA values may indicate re-saved or composited regions."
                if score > 0.4 else "ELA values within normal range."
            ),
        }
    except Exception as exc:
        return {"score": None, "error": str(exc)}


def _compute_noise_consistency(gray: np.ndarray) -> Dict[str, Any]:
    """
    Split image into blocks and measure noise-level variance across blocks.
    AI images often have suspiciously uniform noise patterns.
    """
    try:
        h, w = gray.shape
        block = 64
        noise_vals: List[float] = []

        for r in range(0, h - block, block):
            for c in range(0, w - block, block):
                patch = gray[r:r+block, c:c+block].astype(np.float32)
                # Estimate noise via Laplacian variance
                lap = np.var(np.diff(np.diff(patch, axis=0), axis=1))
                noise_vals.append(float(lap))

        if not noise_vals:
            return {"score": None, "reason": "Image too small for block analysis."}

        consistency = 1.0 - (np.std(noise_vals) / (np.mean(noise_vals) + 1e-6))
        score = round(float(np.clip(consistency, 0, 1)), 4)

        return {
            "score": score,
            "block_noise_std": round(float(np.std(noise_vals)), 3),
            "block_noise_mean": round(float(np.mean(noise_vals)), 3),
            "interpretation": (
                "Unusually uniform noise may indicate AI generation."
                if score > 0.85 else "Noise distribution appears varied (natural)."
            ),
        }
    except Exception as exc:
        return {"score": None, "error": str(exc)}


def _compute_frequency_anomaly(gray: np.ndarray) -> Dict[str, Any]:
    """
    Apply 2-D FFT and measure energy distribution across frequency bands.
    AI-generated images often lack high-frequency detail.
    """
    try:
        f      = np.fft.fft2(gray.astype(np.float32))
        fshift = np.fft.fftshift(f)
        mag    = np.log1p(np.abs(fshift))

        h, w  = mag.shape
        cy, cx = h // 2, w // 2
        r_low  = min(h, w) // 8

        # Mask low-frequency region
        Y, X  = np.ogrid[:h, :w]
        dist  = np.sqrt((X - cx)**2 + (Y - cy)**2)
        low_mask  = dist <= r_low
        high_mask = dist > r_low

        low_energy  = float(np.mean(mag[low_mask]))
        high_energy = float(np.mean(mag[high_mask]))
        ratio       = high_energy / (low_energy + 1e-6)

        # Low ratio → image may lack fine detail (AI signal)
        score = round(float(np.clip(1.0 - ratio * 2, 0, 1)), 4)

        return {
            "score": score,
            "low_freq_energy":  round(low_energy, 4),
            "high_freq_energy": round(high_energy, 4),
            "freq_ratio":       round(ratio, 4),
            "interpretation": (
                "Low high-frequency energy may suggest AI-generated smoothness."
                if score > 0.4 else "Frequency distribution appears natural."
            ),
        }
    except Exception as exc:
        return {"score": None, "error": str(exc)}


def _compute_texture_anomaly(gray: np.ndarray) -> Dict[str, Any]:
    """
    Proxy texture analysis using variance of local standard deviations.
    Unusually smooth textures can indicate AI generation.
    """
    try:
        from PIL import Image as PILImage, ImageFilter

        pil_gray = PILImage.fromarray(gray)
        blurred  = pil_gray.filter(ImageFilter.GaussianBlur(radius=2))
        diff     = np.abs(
            np.array(pil_gray, dtype=np.float32) -
            np.array(blurred, dtype=np.float32)
        )

        local_std  = float(np.std(diff))
        smoothness = 1.0 - min(local_std / 30.0, 1.0)   # normalise

        score = round(float(smoothness), 4)
        return {
            "score": score,
            "local_std": round(local_std, 4),
            "interpretation": (
                "High smoothness detected — may indicate AI-generated textures."
                if score > 0.6 else "Texture variation appears typical for photographs."
            ),
        }
    except Exception as exc:
        return {"score": None, "error": str(exc)}


def _compute_edge_consistency(gray: np.ndarray, cv2: Any) -> Dict[str, Any]:
    """
    Measure edge response consistency using Canny + regional variance.
    AI images can have suspiciously uniform edge distributions.
    """
    try:
        edges      = cv2.Canny(gray, 50, 150)
        h, w       = edges.shape
        block      = 64
        edge_densities: List[float] = []

        for r in range(0, h - block, block):
            for c in range(0, w - block, block):
                patch = edges[r:r+block, c:c+block]
                density = float(np.sum(patch > 0)) / (block * block)
                edge_densities.append(density)

        if not edge_densities:
            return {"score": None, "reason": "Image too small."}

        consistency = 1.0 - float(np.std(edge_densities) / (np.mean(edge_densities) + 1e-6))
        score = round(float(np.clip(consistency, 0, 1)), 4)

        return {
            "score": score,
            "mean_edge_density": round(float(np.mean(edge_densities)), 4),
            "edge_density_std":  round(float(np.std(edge_densities)), 4),
            "interpretation": (
                "Unusually consistent edge distribution — possible AI generation."
                if score > 0.9 else "Edge distribution appears varied (natural)."
            ),
        }
    except Exception as exc:
        return {"score": None, "error": str(exc)}


def _compute_color_distribution(img_np: np.ndarray) -> Dict[str, Any]:
    """
    Analyse per-channel histograms and look for unusual spikes or flat regions.
    """
    try:
        results: Dict[str, Any] = {}
        for i, channel in enumerate(["red", "green", "blue"]):
            ch   = img_np[:, :, i].flatten().astype(np.float32)
            hist = np.histogram(ch, bins=32, range=(0, 255))[0].astype(np.float32)
            hist /= hist.sum() + 1e-6
            entropy = float(-np.sum(hist * np.log2(hist + 1e-10)))
            results[channel] = {
                "mean":    round(float(np.mean(ch)), 2),
                "std":     round(float(np.std(ch)), 2),
                "entropy": round(entropy, 4),
            }
        # Average entropy across channels (natural images > 4 bits)
        avg_entropy = np.mean([results[c]["entropy"] for c in ["red", "green", "blue"]])
        score = round(float(np.clip(1.0 - avg_entropy / 5.0, 0, 1)), 4)

        return {
            "channels": results,
            "score": score,
            "avg_entropy": round(float(avg_entropy), 4),
            "interpretation": (
                "Low color entropy may indicate artificially simplified tones."
                if score > 0.4 else "Color distribution appears natural."
            ),
        }
    except Exception as exc:
        return {"score": None, "error": str(exc)}


# ── Aggregation ────────────────────────────────────────────────────────────────

def _aggregate_anomaly(results: Dict[str, Any]) -> float:
    """
    Weighted average of available anomaly sub-scores.
    Higher score → more anomalies detected (more likely AI-generated).
    """
    weights = {
        "ela":               0.25,
        "noise_consistency": 0.20,
        "frequency_anomaly": 0.20,
        "texture_anomaly":   0.20,
        "edge_consistency":  0.10,
        "color_distribution":0.05,
    }
    total_w = 0.0
    total_s = 0.0
    for key, w in weights.items():
        sub = results.get(key, {})
        score = sub.get("score")
        if score is not None:
            total_s += score * w
            total_w += w

    if total_w == 0:
        return 0.5   # no data — neutral
    return total_s / total_w


def _build_summary(score: float, results: Dict) -> str:
    if score > 0.65:
        level = "significant"
        interp = "Multiple forensic anomalies were detected."
    elif score > 0.40:
        level = "moderate"
        interp = "Some forensic anomalies were detected."
    else:
        level = "minimal"
        interp = "Few forensic anomalies were detected."
    return (
        f"{level.capitalize()} forensic anomaly level (score: {score:.2f}). "
        f"{interp}  This is supporting evidence and not conclusive proof."
    )


def _build_chart_data(results: Dict) -> List[Dict]:
    """Build a list of {name, score} for chart rendering on the frontend."""
    labels = {
        "ela":               "ELA",
        "noise_consistency": "Noise Consistency",
        "frequency_anomaly": "Frequency Anomaly",
        "texture_anomaly":   "Texture Anomaly",
        "edge_consistency":  "Edge Consistency",
        "color_distribution":"Color Distribution",
    }
    chart = []
    for key, label in labels.items():
        sub = results.get(key, {})
        s   = sub.get("score")
        if s is not None:
            chart.append({"name": label, "score": round(float(s), 4)})
    return chart


def _cv2_unavailable() -> Dict[str, Any]:
    return {
        "status": "unavailable",
        "anomaly_score": None,
        "details": {},
        "summary": "OpenCV is not installed. Forensic analysis is unavailable.",
        "chart_data": [],
        "limitations": "Install opencv-python-headless to enable forensic analysis.",
    }

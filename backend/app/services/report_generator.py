"""Report generator — assembles all sub-results into a structured report dict."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def generate_report(
    analysis_id: str,
    file_info: Dict[str, Any],
    metadata_result: Dict[str, Any],
    provenance_result: Dict[str, Any],
    watermark_result: Dict[str, Any],
    visual_result: Dict[str, Any],
    forensic_result: Dict[str, Any],
    fusion_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a complete, structured analysis report.
    """
    return {
        "report_version": "1.0",
        "analysis_id": analysis_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "file_info": {
            "original_filename": file_info.get("original_filename"),
            "file_size":         file_info.get("file_size"),
            "file_type":         file_info.get("file_type"),
            "mime_type":         file_info.get("mime_type"),
            "image_width":       file_info.get("image_width"),
            "image_height":      file_info.get("image_height"),
        },
        "final_verdict": {
            "classification":  fusion_result.get("final_result"),
            "ai_probability":  fusion_result.get("ai_probability"),
            "real_probability":fusion_result.get("real_probability"),
            "confidence_score":fusion_result.get("confidence_score"),
            "summary":         fusion_result.get("summary"),
            "disclaimer":      fusion_result.get("disclaimer"),
        },
        "evidence": {
            "metadata":   metadata_result,
            "provenance": provenance_result,
            "watermark":  watermark_result,
            "visual_ai":  visual_result,
            "forensics":  forensic_result,
        },
        "fusion_details": {
            "contributions":       fusion_result.get("contributions"),
            "weights_used":        fusion_result.get("weights_used"),
            "positive_indicators": fusion_result.get("positive_indicators"),
            "negative_indicators": fusion_result.get("negative_indicators"),
            "thresholds":          fusion_result.get("thresholds"),
        },
        "limitations": [
            "This result is an estimation and should not be used as legal evidence.",
            "Metadata can be stripped, edited, or fabricated.",
            "Absence of C2PA credentials does not indicate AI generation.",
            "The AI model was trained on a specific dataset and may not generalise to all generators.",
            "Forensic signals can be triggered by compression, editing, or resizing.",
            "No system can detect AI-generated images with 100% accuracy.",
        ],
    }

"""
Visual Detector — EfficientNet-B0 based AI vs Real image classifier.

If the trained model file (models/image_detector.pt) is not present,
this module returns "model_not_configured" and instructions for training.

IMPORTANT:
  This module does NOT produce random predictions.
  If the model is unavailable it clearly reports that fact.
"""
from __future__ import annotations

import json
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

MODEL_NAME    = "EfficientNet-B0"
MODEL_VERSION = "1.0"
INPUT_SIZE    = 224   # pixels


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_visual(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Run the AI / Real classifier on raw image bytes.
    Returns a structured prediction dict.
    """
    model = _get_model()
    if model is None:
        return _model_unavailable_response()

    try:
        import torch
        import torchvision.transforms as T

        transform = T.Compose([
            T.Resize((INPUT_SIZE, INPUT_SIZE)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]),
        ])

        img = Image.open(BytesIO(raw_bytes)).convert("RGB")
        tensor = transform(img).unsqueeze(0)  # shape: [1, 3, H, W]

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        tensor = tensor.to(device)

        model.eval()
        with torch.no_grad():
            logits = model(tensor)           # shape: [1, 2]
            probs  = torch.softmax(logits, dim=1)[0]

        real_prob = float(probs[0].item())
        ai_prob   = float(probs[1].item())
        prediction = "ai_generated" if ai_prob > real_prob else "real"

        return {
            "status": "success",
            "prediction": prediction,
            "ai_probability": round(ai_prob, 4),
            "real_probability": round(real_prob, 4),
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "device_used": str(device),
            "limitations": (
                "This model was trained on a specific dataset and may not generalise "
                "perfectly to all AI generators or photography styles. "
                "The confidence score is an estimate, not a definitive verdict."
            ),
        }

    except Exception as exc:
        logger.error("Visual detector inference failed: %s", exc, exc_info=True)
        return {
            "status": "error",
            "prediction": None,
            "ai_probability": None,
            "real_probability": None,
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "error": str(exc),
            "limitations": "Model inference failed. See server logs.",
        }


# ── Model loading ─────────────────────────────────────────────────────────────

_cached_model = None   # module-level cache so the model is loaded only once


def _get_model() -> Optional[Any]:
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    if not settings.MODEL_PATH.exists():
        logger.warning(
            "Model file not found at %s. "
            "Run train_model.py to train and save the model.",
            settings.MODEL_PATH,
        )
        return None

    try:
        import torch
        import torchvision.models as models

        # Build the same architecture used during training
        net = models.efficientnet_b0(weights=None)
        # Replace the classifier head: 2 output classes (real / ai_generated)
        import torch.nn as nn
        in_features = net.classifier[1].in_features
        net.classifier[1] = nn.Linear(in_features, 2)

        state = torch.load(settings.MODEL_PATH, map_location="cpu")
        net.load_state_dict(state)
        net.eval()
        _cached_model = net
        logger.info("Visual detection model loaded from %s", settings.MODEL_PATH)
        return _cached_model

    except Exception as exc:
        logger.error("Failed to load model: %s", exc, exc_info=True)
        return None


def _model_unavailable_response() -> Dict[str, Any]:
    return {
        "status": "model_not_configured",
        "prediction": None,
        "ai_probability": None,
        "real_probability": None,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "instructions": (
            "To enable AI visual detection:\n"
            "1. Prepare a dataset of real and AI-generated images.\n"
            "2. Run: python backend/train_model.py\n"
            "3. The trained model will be saved to backend/models/image_detector.pt\n"
            "4. Restart the backend server.\n"
            "See backend/train_model.py for dataset format and training options."
        ),
        "limitations": (
            "The AI visual detection model is not configured. "
            "The overall analysis still uses metadata, provenance, and forensic signals."
        ),
    }

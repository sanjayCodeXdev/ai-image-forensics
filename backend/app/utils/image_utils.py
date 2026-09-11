"""Image utility helpers (resizing, format conversion, validation)."""
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, UnidentifiedImageError


def open_image_safely(data: bytes) -> Optional[Image.Image]:
    """
    Attempt to open image bytes. Returns None if the data is not a valid image.
    Uses Pillow's strict mode to reject truncated / corrupted files.
    """
    try:
        img = Image.open(BytesIO(data))
        img.verify()          # raises on corruption
        # Re-open after verify (verify() closes the stream)
        img = Image.open(BytesIO(data))
        img.load()            # force full decode
        return img
    except (UnidentifiedImageError, Exception):
        return None


def get_image_dimensions(data: bytes) -> Optional[Tuple[int, int]]:
    """Return (width, height) or None if image is invalid."""
    img = open_image_safely(data)
    if img is None:
        return None
    return img.size


def resize_for_analysis(img: Image.Image, max_side: int = 1024) -> Image.Image:
    """
    Resize image so that the longest side <= max_side, preserving aspect ratio.
    Returns a copy — does not mutate the original.
    """
    w, h = img.size
    if max(w, h) <= max_side:
        return img.copy()
    scale = max_side / max(w, h)
    new_size = (int(w * scale), int(h * scale))
    return img.resize(new_size, Image.LANCZOS)


def to_rgb(img: Image.Image) -> Image.Image:
    """Ensure image is in RGB mode (needed for ML model input)."""
    if img.mode != "RGB":
        return img.convert("RGB")
    return img

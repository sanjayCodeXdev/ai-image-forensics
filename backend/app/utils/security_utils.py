"""Security utilities — safe filename generation and path validation."""
import re
import uuid
from pathlib import Path


def generate_safe_filename(original_name: str) -> str:
    """
    Return a UUID-based filename preserving the original extension.
    This prevents path traversal and execution of uploaded files.
    """
    suffix = Path(original_name).suffix.lower()
    # Whitelist only expected image extensions
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
    if suffix not in allowed:
        suffix = ".bin"
    return f"{uuid.uuid4().hex}{suffix}"


def is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """Ensure target_path is strictly under base_dir (prevent path traversal)."""
    try:
        target_path.resolve().relative_to(base_dir.resolve())
        return True
    except ValueError:
        return False


def sanitize_display_filename(name: str) -> str:
    """Strip everything except safe characters for display purposes."""
    name = Path(name).name          # remove any directory component
    name = re.sub(r"[^\w.\- ]", "_", name)
    return name[:255]               # cap length

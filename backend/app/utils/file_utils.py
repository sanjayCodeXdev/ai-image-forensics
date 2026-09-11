"""File-system utilities for upload handling."""
import aiofiles
from pathlib import Path


async def save_upload(source_bytes: bytes, dest_path: Path) -> None:
    """Write raw bytes to dest_path asynchronously."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(dest_path, "wb") as f:
        await f.write(source_bytes)


async def delete_file(path: Path) -> bool:
    """Delete a file; return True on success, False if not found."""
    try:
        path.unlink()
        return True
    except FileNotFoundError:
        return False


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

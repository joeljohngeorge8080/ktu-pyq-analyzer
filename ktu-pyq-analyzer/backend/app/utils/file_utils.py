import os
import re
import uuid
from pathlib import Path
from fastapi import HTTPException

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}

def validate_file(filename: str, content_type: str, size_bytes: int, max_mb: int = 50):
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type '{ext}' not allowed. Use PDF, JPG, PNG.")
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"MIME type '{content_type}' not allowed.")
    if size_bytes > max_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {max_mb}MB limit.")

def safe_filename(filename: str) -> str:
    """Sanitize filename and prepend UUID to avoid collisions and path traversal."""
    name = Path(filename).stem
    ext = Path(filename).suffix.lower()
    # Remove any path traversal chars
    name = re.sub(r"[^\w\-]", "_", name)
    return f"{uuid.uuid4().hex}_{name}{ext}"

def ensure_dirs(*paths: Path):
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)

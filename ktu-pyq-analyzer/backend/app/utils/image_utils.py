"""
Image utilities using Pillow only — no OpenCV dependency.
All cropping is handled client-side (canvas) and arrives as base64 PNG.
These server-side helpers are for PDF page rendering and page counting.
"""
from pathlib import Path
from PIL import Image
import io


def crop_image_region(image_path: str, x: int, y: int, w: int, h: int, out_path: str) -> str:
    """Crop a rectangular region from an image using Pillow."""
    img = Image.open(image_path)
    iw, ih = img.size
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(iw, x + w)
    y2 = min(ih, y + h)
    cropped = img.crop((x1, y1, x2, y2))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    cropped.save(out_path, "PNG")
    return out_path


def pdf_page_to_image(pdf_path: str, page_num: int, out_path: str, dpi: int = 150) -> str:
    """Convert a single PDF page to a PNG image using pdf2image (poppler)."""
    from pdf2image import convert_from_path
    pages = convert_from_path(
        pdf_path, dpi=dpi, first_page=page_num, last_page=page_num
    )
    if not pages:
        raise RuntimeError(f"No pages returned for page {page_num}")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(out_path, "PNG")
    return out_path


def get_pdf_page_count(pdf_path: str) -> int:
    """Return number of pages in a PDF."""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        return len(reader.pages)
    except Exception:
        return 1

import os
import io
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from app.database.base import get_db
from app.models import Paper
from app.schemas.paper import PaperOut
from app.services.paper_service import upload_paper
from app.config import settings

router = APIRouter(prefix="/papers", tags=["Papers"])


@router.post("/upload", response_model=PaperOut, status_code=201)
async def upload(
    file: UploadFile = File(...),
    subject_name: str = Form(...),
    year: int = Form(...),
    exam_type: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    return await upload_paper(db, file, subject_name, year, exam_type)


@router.get("", response_model=List[PaperOut])
def list_papers(
    subject_id: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Paper)
    if subject_id:
        q = q.filter(Paper.subject_id == subject_id)
    if year:
        q = q.filter(Paper.year == year)
    return q.order_by(Paper.uploaded_at.desc()).all()


@router.get("/{paper_id}", response_model=PaperOut)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(404, "Paper not found")
    return paper


@router.get("/{paper_id}/page/{page_num}")
def get_paper_page_image(paper_id: int, page_num: int, db: Session = Depends(get_db)):
    """
    Render a single PDF page as PNG and return it.
    For image uploads, returns the image directly (page_num ignored).
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(404, "Paper not found")

    abs_path = str(settings.upload_path / paper.file_path)

    if paper.file_type == "image":
        # Serve image directly
        with open(abs_path, "rb") as f:
            data = f.read()
        ext = Path(paper.file_path).suffix.lower().lstrip(".")
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png", "webp": "image/webp"}.get(ext, "image/png")
        return Response(content=data, media_type=mime)

    # PDF: render requested page
    if page_num < 1 or page_num > paper.page_count:
        raise HTTPException(400, f"Page {page_num} out of range (1–{paper.page_count})")

    # Cache rendered pages in uploads/page_cache/
    cache_dir = settings.upload_path / "page_cache" / str(paper_id)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"page_{page_num}.png"

    if not cache_file.exists():
        try:
            from app.utils.image_utils import pdf_page_to_image
            pdf_page_to_image(abs_path, page_num, str(cache_file))
        except Exception as e:
            raise HTTPException(500, f"Could not render PDF page: {e}")

    with open(cache_file, "rb") as f:
        data = f.read()
    return Response(content=data, media_type="image/png")


@router.delete("/{paper_id}", status_code=204)
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(404, "Paper not found")
    db.delete(paper)
    db.commit()

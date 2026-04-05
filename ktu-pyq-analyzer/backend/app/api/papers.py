import logging
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from app.database.base import get_db
from app.models import Paper
from app.schemas.paper import PaperOut
from app.services.paper_service import upload_paper
from app.config import settings

logger = logging.getLogger(__name__)
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
    """Render a single PDF page as PNG and return it."""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(404, "Paper not found")

    abs_path = str(settings.upload_path / paper.file_path)

    if paper.file_type == "image":
        with open(abs_path, "rb") as f:
            data = f.read()
        ext = Path(paper.file_path).suffix.lower().lstrip(".")
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png", "webp": "image/webp"}.get(ext, "image/png")
        return Response(content=data, media_type=mime)

    if page_num < 1 or page_num > paper.page_count:
        raise HTTPException(400, f"Page {page_num} out of range (1–{paper.page_count})")

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


@router.post("/{paper_id}/process")
def process_paper(paper_id: int, db: Session = Depends(get_db)):
    """
    Trigger the 3-stage layout-aware question parser.
    Returns structured debug info along with success status.
    """
    from app.services.question_parser import parse_paper
    from app.models import Question

    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(404, "Paper not found")

    try:
        logger.info(f"Processing paper {paper_id}…")
        success = parse_paper(db, paper_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.exception(f"Parsing failed for paper {paper_id}")
        raise HTTPException(500, f"Processing error: {e}")

    # Build response with per-question summary
    questions = db.query(Question).filter(Question.paper_id == paper_id).all()
    summary = [
        {
            "question_number": q.question_number,
            "module": q.module,
            "type": q.type,
            "page": q.page_number,
            "has_image": bool(q.image_path),
        }
        for q in sorted(questions, key=lambda x: int(x.question_number or 0))
    ]

    return {
        "status": "success" if success else "partial",
        "paper_id": paper_id,
        "total_questions": len(questions),
        "short_questions": sum(1 for q in questions if q.type == "short"),
        "long_questions": sum(1 for q in questions if q.type == "long"),
        "questions": summary,
    }


@router.get("/{paper_id}/parse-debug")
def parse_debug(paper_id: int, db: Session = Depends(get_db)):
    """
    Dry-run the parser and return detected sections + question positions
    WITHOUT saving to DB. Useful for diagnosing detection issues.
    """
    from app.services.question_parser import (
        load_pages, detect_sections,
        detect_short_questions, detect_long_questions,
    )

    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(404, "Paper not found")

    try:
        pages = load_pages(paper)
        sections = detect_sections(pages)

        part_a = next((s for s in sections if s.label == "PART_A"), None)
        part_b = next((s for s in sections if s.label == "PART_B"), None)

        if not part_a:
            part_a_page, part_a_y = 1, 0
        else:
            part_a_page, part_a_y = part_a.page, part_a.y

        if not part_b:
            part_b_page = 1
            part_b_y = pages[0].height // 2
        else:
            part_b_page, part_b_y = part_b.page, part_b.y

        short_qs = detect_short_questions(pages, part_a_page, part_a_y, part_b_page, part_b_y)
        long_qs = detect_long_questions(pages, sections)

    except Exception as e:
        logger.exception("parse-debug failed")
        raise HTTPException(500, str(e))

    return {
        "pages": len(pages),
        "sections": [
            {"label": s.label, "page": s.page, "y": s.y, "module": s.module_num}
            for s in sections
        ],
        "short_questions_detected": [
            {"q": dq.question_number, "page": dq.page,
             "bbox": [dq.x_start, dq.y_start, dq.x_end, dq.y_end]}
            for dq in short_qs
        ],
        "long_questions_detected": [
            {"q": dq.question_number, "module": dq.module, "page": dq.page,
             "bbox": [dq.x_start, dq.y_start, dq.x_end, dq.y_end],
             "subparts": dq.subparts}
            for dq in long_qs
        ],
    }


@router.delete("/{paper_id}", status_code=204)
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(404, "Paper not found")
    db.delete(paper)
    db.commit()

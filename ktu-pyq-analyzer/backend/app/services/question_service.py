import base64
import io
import tempfile
import os
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Question, Paper
from app.schemas.question import QuestionCreate
from app.utils.image_utils import crop_image_region
from app.utils.file_utils import safe_filename
from app.services.storage import storage
from app.config import settings


def save_cropped_question(
    db: Session,
    data: QuestionCreate,
    image_b64: str,       # base64-encoded PNG of the cropped region
) -> Question:
    paper = db.query(Paper).filter(Paper.id == data.paper_id).first()
    if not paper:
        raise HTTPException(404, "Paper not found")

    # Decode base64 image
    try:
        img_bytes = base64.b64decode(image_b64)
    except Exception:
        raise HTTPException(400, "Invalid base64 image data")

    dest_key = f"questions/paper_{data.paper_id}_mod{data.module}_{safe_filename('crop.png')}"
    abs_path = storage.save_bytes(img_bytes, dest_key)

    question = Question(
        paper_id=data.paper_id,
        module=data.module,
        type=data.type,
        question_number=data.question_number,
        image_path=dest_key,
        tags=data.tags or [],
        page_number=data.page_number or 1,
        crop_coords=data.crop_coords,
        notes=data.notes,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_questions_filtered(
    db: Session,
    subject_id: int | None = None,
    module: int | None = None,
    q_type: str | None = None,
    year: int | None = None,
    paper_id: int | None = None,
):
    from app.models import Paper
    q = db.query(Question).join(Paper)
    if subject_id:
        q = q.filter(Paper.subject_id == subject_id)
    if module:
        q = q.filter(Question.module == module)
    if q_type:
        q = q.filter(Question.type == q_type)
    if year:
        q = q.filter(Paper.year == year)
    if paper_id:
        q = q.filter(Question.paper_id == paper_id)
    return q.order_by(Question.created_at.desc()).all()

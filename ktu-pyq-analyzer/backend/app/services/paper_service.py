import os
import shutil
import tempfile
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from app.models import Paper, Subject
from app.config import settings
from app.utils.file_utils import validate_file, safe_filename, ensure_dirs
from app.utils.image_utils import get_pdf_page_count
from app.services.storage import storage


def create_or_get_subject(db: Session, name: str, code: str | None = None) -> Subject:
    subject = db.query(Subject).filter(Subject.name == name).first()
    if not subject:
        subject = Subject(name=name, code=code)
        db.add(subject)
        db.commit()
        db.refresh(subject)
    return subject


async def upload_paper(
    db: Session,
    file: UploadFile,
    subject_name: str,
    year: int,
    exam_type: str | None = None,
) -> Paper:
    content = await file.read()
    validate_file(file.filename, file.content_type, len(content))

    subject = create_or_get_subject(db, subject_name)

    safe_name = safe_filename(file.filename)
    ext = Path(file.filename).suffix.lower()
    file_type = "pdf" if ext == ".pdf" else "image"
    dest_key = f"papers/{safe_name}"

    # Write to temp then copy via storage
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        abs_path = storage.save(tmp_path, dest_key)
        page_count = 1
        if file_type == "pdf":
            try:
                page_count = get_pdf_page_count(abs_path)
            except Exception:
                page_count = 1
    finally:
        os.unlink(tmp_path)

    paper = Paper(
        subject_id=subject.id,
        year=year,
        exam_type=exam_type,
        file_path=dest_key,
        original_filename=file.filename,
        file_type=file_type,
        page_count=page_count,
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return paper

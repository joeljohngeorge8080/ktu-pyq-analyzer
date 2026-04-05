import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import zipfile
import tempfile
from pathlib import Path

from app.database.base import get_db
from app.models import Question, Subject, Paper
from app.config import settings

router = APIRouter(prefix="/download", tags=["Downloads"])

@router.get("/module")
def download_module(subject_id: int, module: int, year: int = None, db: Session = Depends(get_db)):
    """Download all questions for a specific module of a subject"""
    q_query = db.query(Question).join(Paper).filter(
        Paper.subject_id == subject_id,
        Question.module == module
    )
    if year:
        q_query = q_query.filter(Paper.year == year)
        
    questions = q_query.all()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this module")
        
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    sub_name = subject.name.replace(" ", "_") if subject else "subject"
    
    # Create temp zip file
    tmp_path = Path(tempfile.gettempdir()) / f"module_{module}_{sub_name}.zip"
    
    with zipfile.ZipFile(tmp_path, "w") as zf:
        for q in questions:
            img_path = settings.upload_path / q.image_path
            if img_path.exists():
                arcname = f"Year_{q.paper.year}/{q.type}_Q{q.question_number}_{q.id}.png"
                zf.write(img_path, arcname)
                
    return FileResponse(tmp_path, media_type="application/zip", filename=tmp_path.name)

@router.get("/subject")
def download_subject(subject_id: int, db: Session = Depends(get_db)):
    """Download entire subject dataset"""
    questions = db.query(Question).join(Paper).filter(Paper.subject_id == subject_id).all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this subject")
        
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    sub_name = subject.name.replace(" ", "_") if subject else "subject"
    
    tmp_path = Path(tempfile.gettempdir()) / f"{sub_name}_complete.zip"
    
    with zipfile.ZipFile(tmp_path, "w") as zf:
        for q in questions:
            img_path = settings.upload_path / q.image_path
            if img_path.exists():
                arcname = f"Module_{q.module}/Year_{q.paper.year}/{q.type}_Q{q.question_number}_{q.id}.png"
                zf.write(img_path, arcname)
                
    return FileResponse(tmp_path, media_type="application/zip", filename=tmp_path.name)

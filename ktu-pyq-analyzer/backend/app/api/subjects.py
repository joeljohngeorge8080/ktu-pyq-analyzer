from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.models import Subject
from app.schemas.subject import SubjectCreate, SubjectOut
from typing import List

router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.post("", response_model=SubjectOut, status_code=201)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    existing = db.query(Subject).filter(Subject.name == payload.name).first()
    if existing:
        raise HTTPException(409, "Subject already exists")
    s = Subject(name=payload.name, code=payload.code)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@router.get("", response_model=List[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).order_by(Subject.name).all()

@router.get("/{subject_id}", response_model=SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    s = db.query(Subject).filter(Subject.id == subject_id).first()
    if not s:
        raise HTTPException(404, "Subject not found")
    return s

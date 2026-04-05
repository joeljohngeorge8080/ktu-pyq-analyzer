from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database.base import get_db
from app.schemas.question import QuestionCreate, QuestionOut
from app.services.question_service import save_cropped_question, get_questions_filtered

router = APIRouter(prefix="/questions", tags=["Questions"])

class CropPayload(BaseModel):
    metadata: QuestionCreate
    image_b64: str  # base64 PNG

@router.post("", response_model=QuestionOut, status_code=201)
def create_question(payload: CropPayload, db: Session = Depends(get_db)):
    return save_cropped_question(db, payload.metadata, payload.image_b64)

@router.get("", response_model=List[QuestionOut])
def list_questions(
    subject_id: Optional[int] = None,
    paper_id: Optional[int] = None,
    module: Optional[int] = None,
    type: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return get_questions_filtered(db, subject_id, module, type, year, paper_id)

@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    from app.models import Question
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(404, "Question not found")
    return q

@router.delete("/{question_id}", status_code=204)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    from app.models import Question
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(404, "Question not found")
    db.delete(q)
    db.commit()

@router.put("/{question_id}", response_model=QuestionOut)
def update_question(question_id: int, payload: dict, db: Session = Depends(get_db)):
    from app.models import Question
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(404, "Question not found")
    
    if "module" in payload:
        q.module = payload["module"]
    if "type" in payload:
        q.type = payload["type"]
    if "question_number" in payload:
        q.question_number = payload["question_number"]
        
    db.commit()
    db.refresh(q)
    return q


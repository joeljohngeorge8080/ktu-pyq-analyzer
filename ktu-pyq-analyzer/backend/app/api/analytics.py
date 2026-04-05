from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from collections import Counter, defaultdict

from app.database.base import get_db
from app.models import Question, Paper, Subject

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/frequency")
def frequency_analysis(
    subject_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Return tag/topic frequency and module distribution."""
    q = db.query(Question).join(Paper)
    if subject_id:
        q = q.filter(Paper.subject_id == subject_id)
    questions = q.all()

    tag_counter: Counter = Counter()
    module_dist: dict = defaultdict(lambda: {"short": 0, "long": 0, "total": 0})
    year_dist: dict = defaultdict(int)

    for question in questions:
        paper = question.paper
        year_dist[paper.year] += 1
        module_dist[question.module][question.type] += 1
        module_dist[question.module]["total"] += 1
        for tag in (question.tags or []):
            tag_counter[str(tag)] += 1

    top_tags = [{"tag": t, "count": c} for t, c in tag_counter.most_common(20)]

    return {
        "total_questions": len(questions),
        "top_tags": top_tags,
        "module_distribution": {
            f"Module {k}": v for k, v in sorted(module_dist.items())
        },
        "year_distribution": dict(sorted(year_dist.items())),
    }

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    subjects = db.query(Subject).count()
    papers = db.query(Paper).count()
    questions = db.query(Question).count()
    return {"subjects": subjects, "papers": papers, "questions": questions}

from fastapi import APIRouter
from .subjects import router as subjects_router
from .papers import router as papers_router
from .questions import router as questions_router
from .analytics import router as analytics_router
from .downloads import router as downloads_router

api_router = APIRouter()
api_router.include_router(subjects_router)
api_router.include_router(papers_router)
api_router.include_router(questions_router)
api_router.include_router(analytics_router)
api_router.include_router(downloads_router)

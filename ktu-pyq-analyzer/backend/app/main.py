from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from app.config import settings
from app.database.base import Base, engine
from app.api import api_router
import app.models  # noqa: F401 — ensure models are registered

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables + upload dirs on startup
    Base.metadata.create_all(bind=engine)
    settings.papers_path.mkdir(parents=True, exist_ok=True)
    settings.questions_path.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(
    title="KTU PYQ Analyzer API",
    description="Previous Year Question Paper analyzer for KTU students",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
upload_path = settings.upload_path
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(upload_path)), name="static")

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

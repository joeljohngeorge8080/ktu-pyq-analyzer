import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import settings
from app.database.base import Base, engine
from app.api import api_router
import app.models  # noqa: F401

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
# Make the parser very verbose during development
logging.getLogger("app.services.question_parser").setLevel(logging.DEBUG)
logging.getLogger("app.services.ocr_service").setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    settings.papers_path.mkdir(parents=True, exist_ok=True)
    settings.questions_path.mkdir(parents=True, exist_ok=True)
    (settings.upload_path / "page_cache").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="KTU PYQ Analyzer API",
    description="Previous Year Question Paper analyzer for KTU students",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_path = settings.upload_path
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(upload_path)), name="static")

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

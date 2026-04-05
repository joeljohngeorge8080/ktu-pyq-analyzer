# 📚 KTU PYQ Analyzer

A production-ready web application for KTU students to upload, crop, tag, and analyze previous year question papers.

## ✨ Features

- **Upload Papers** — PDF or image files with subject/year metadata
- **Viewer & Crop Tool** — Draw rectangles to select questions from any page
- **Smart Tagging** — Tag by Module (1–5), Type (Short/Long), Question Number & custom tags
- **Organized Browse** — View questions grouped by Subject → Module → Type → Year
- **Analytics** — Topic frequency charts, module/year distribution, top repeated topics
- **Modular Storage** — Local filesystem with easy S3 swap

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, SQLAlchemy, PostgreSQL |
| Frontend | React (Vite), Tailwind CSS, Recharts |
| Image Processing | OpenCV, Pillow |
| Deployment | Docker, Nginx, Gunicorn/Uvicorn |

## 🚀 Quick Start

### With Docker (Recommended)

```bash
git clone <repo>
cd ktu-pyq-analyzer
docker compose up --build
```

Open http://localhost — done!

### Manual Setup

**Backend:**
```bash
cd backend
cp .env.example .env   # edit DATABASE_URL
pip install -r requirements.txt
pip install pdf2image pypdf
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database:** Ensure PostgreSQL is running with credentials matching `.env`.

## 🧪 Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/papers/upload` | Upload a paper |
| GET | `/api/v1/papers` | List papers |
| POST | `/api/v1/questions` | Save cropped question |
| GET | `/api/v1/questions` | List questions (filterable) |
| GET | `/api/v1/analytics/frequency` | Topic frequency |
| GET | `/api/v1/analytics/overview` | Dashboard stats |

Interactive docs: http://localhost:8000/docs

## 📁 Project Structure

```
ktu-pyq-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── utils/        # File & image helpers
│   │   └── main.py
│   └── tests/
└── frontend/
    └── src/
        ├── components/   # Reusable UI + crop tool
        ├── pages/        # Dashboard, Upload, Viewer, Browse, Analytics
        ├── services/     # API client
        └── hooks/        # useApi
```

## 🔐 Security

- File type validation (MIME + extension)
- 50MB file size limit
- UUID-prefixed filenames (path traversal prevention)
- Input sanitization via Pydantic validators

## ☁️ Deploying to Production

1. Set `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_ORIGINS` as env vars
2. Replace `LocalStorage` with `S3Storage` in `services/storage.py`
3. `docker compose -f docker-compose.yml up -d`


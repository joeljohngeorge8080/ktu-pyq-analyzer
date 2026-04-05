FROM python:3.11-slim

# System dependencies:
#   poppler-utils  — for pdf2image (PDF→image)
#   tesseract-ocr  — for pytesseract OCR
#   tesseract-ocr-eng — English language pack
#   libgl1         — OpenCV runtime (fallback)
#   libglib2.0-0   — required by some image libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pin numpy<2 BEFORE any other pip installs to prevent NumPy 2.x from resolving
RUN pip install --no-cache-dir "numpy<2"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads/papers uploads/questions uploads/page_cache

EXPOSE 8000

CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--preload"]

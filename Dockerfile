FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    netcat-openbsd \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    tesseract-ocr \
    poppler-utils \
    ghostscript \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH="/app"

COPY pyproject.toml ./
COPY rag_engine /app/rag_engine
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

RUN pip install --upgrade pip && pip install .

EXPOSE 8000

CMD ["gunicorn", "api_service.wsgi:application", "--bind", "0.0.0.0:8000"]

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TREND_TO_COMMERCE_DATA_DIR=/app/Data \
    TREND_TO_COMMERCE_DB_PATH=/app/storage/trend_to_commerce.db

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY web /app/web
COPY Data /app/Data

RUN mkdir -p /app/storage

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY shared ./shared
COPY backend/services/ingestion_service ./ingestion_service

WORKDIR /app/ingestion_service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8003

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]

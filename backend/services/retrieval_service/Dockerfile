FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY shared ./shared
COPY backend/services/retrieval_service ./retrieval_service

WORKDIR /app/retrieval_service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]


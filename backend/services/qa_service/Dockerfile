FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY shared ./shared
COPY backend/services/qa_service ./qa_service

WORKDIR /app/qa_service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8002

CMD ["uvicorn", "qa_service.app:app", "--host", "0.0.0.0", "--port", "8002"]


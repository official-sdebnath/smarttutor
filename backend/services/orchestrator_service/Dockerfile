FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY shared ./shared
COPY backend/services/orchestrator_service ./orchestrator_service

WORKDIR /app/orchestrator_service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8006

CMD ["uvicorn", "orchestrator_service.app:app", "--host", "0.0.0.0", "--port", "8006"]

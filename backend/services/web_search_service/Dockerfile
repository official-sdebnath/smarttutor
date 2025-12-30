FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY shared ./shared
COPY backend/services/web_search_service ./web_search_service

WORKDIR /app/web_search_service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8004

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8004"]

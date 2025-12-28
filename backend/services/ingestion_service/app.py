from fastapi import FastAPI
from shared.schemas.ingestion import IngestRequest, IngestResponse
from .service import ingest_directory

app = FastAPI(title="SmartTutor Ingestion Service")


@app.get("/")
def root():
    return {"service": "ingestion", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    count = ingest_directory(req.path)
    return IngestResponse(ingested_chunks=count)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)

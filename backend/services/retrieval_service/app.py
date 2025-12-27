from fastapi import FastAPI

from .search import search_chunks
from shared.schemas.retrieval import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedChunk,
)

app = FastAPI(title="SmartTutor Retrieval Service")


@app.get("/")
def root():
    return {"service": "retrieval", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/retrieve", response_model=RetrievalResponse)
def retrieve(req: RetrievalRequest):
    results = search_chunks(req.query, req.k)

    top_score = results[0]["score"] if results else 0.0

    return RetrievalResponse(
        items=[
            RetrievedChunk(
                text=r["text"],
                metadata=r["metadata"],
                score=r["score"],
            )
            for r in results
        ],
        top_score=float(top_score),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)

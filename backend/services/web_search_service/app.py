from fastapi import FastAPI
from shared.schemas.web_search import WebSearchRequest, WebSearchResponse
from .service import search_and_synthesize

app = FastAPI(title="SmartTutor Web Search Service")


@app.get("/")
def root():
    return {"service": "web_search", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search", response_model=WebSearchResponse)
def search(req: WebSearchRequest):
    result = search_and_synthesize(req.query, k=req.k)
    return WebSearchResponse(
        answer=result["answer"],
        items=result["items"],
        top_score=result["top_score"],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)

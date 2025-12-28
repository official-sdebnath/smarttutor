from fastapi import FastAPI
from shared.schemas.orchestrator import ChatRequest, ReviewRequest, ChatResponse
from .service import Orchestrator
from utils.utils import configure_dspy

app = FastAPI(title="SmartTutor Orchestrator Service")

orchestrator = Orchestrator()


@app.get("/")
def root():
    return {"message": "SmartTutor Orchestrator Service"}


@app.on_event("startup")
def startup():
    configure_dspy()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = orchestrator.run(
        user_input=req.message,
        thread_id=req.thread_id,
        user_id=req.user_id,
    )

    if isinstance(result, dict) and result.get("needs_review"):
        return ChatResponse(
            needs_review=True,
            current_answer=result["current_answer"],
        )

    return ChatResponse(answer=result["final_answer"])


@app.post("/review", response_model=ChatResponse)
def review(req: ReviewRequest):
    result = orchestrator.run(
        user_input="",
        thread_id=req.thread_id,
        user_id=req.user_id,
        human_feedback=req.feedback,
    )
    return ChatResponse(answer=result["final_answer"])


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8006)

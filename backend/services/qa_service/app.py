from fastapi import FastAPI

from shared.schemas.qa import QARequest, QAResponse
from backend.services.qa_service.qa import answer_question

app = FastAPI(title="SmartTutor QA Service")


@app.get("/")
def root():
    return {"message": "SmartTutor QA Service"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=QAResponse)
def ask(req: QARequest):
    result = answer_question(
        question=req.question,
        conversation_context=req.conversation_context,
        k=req.k,
    )
    return QAResponse(**result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)

from fastapi import APIRouter
from models.models import QARequest, QAResponse
from backend.services.qa import answer_question

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("/query", response_model=QAResponse)
def ask_question(body: QARequest):
    result = answer_question(body.question, k=body.top_k)
    return QAResponse(answer=result["answer"], sources=result["sources"])

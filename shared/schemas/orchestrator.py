from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    thread_id: str
    user_id: str


class ReviewRequest(BaseModel):
    thread_id: str
    user_id: str
    feedback: str


class ChatResponse(BaseModel):
    answer: Optional[str] = None
    needs_review: bool = False
    current_answer: Optional[str] = None


class EvalResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Evaluation score between 0 and 1")

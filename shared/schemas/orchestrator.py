from pydantic import BaseModel
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

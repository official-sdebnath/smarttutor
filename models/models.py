from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

class ChatMessage(BaseModel):
    user_id: str
    session_id: str
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime

class QARequest(BaseModel):
    question: str
    top_k: int = 5


class SourceItem(BaseModel):
    source: str | None = None
    page: int | None = None
    chunk_index: int | None = None


class QAResponse(BaseModel):
    answer: str
    sources: List[SourceItem]


class EvalResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Evaluation score between 0 and 1")

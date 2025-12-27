from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class QARequest(BaseModel):
    question: str
    conversation_context: Optional[str] = None
    k: int = 5


class QAResponse(BaseModel):
    answer: str
    items: List[Dict[str, Any]]
    top_score: float

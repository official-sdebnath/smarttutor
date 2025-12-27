from pydantic import BaseModel
from typing import List, Dict, Any


class RetrievalRequest(BaseModel):
    query: str
    k: int = 5


class RetrievedChunk(BaseModel):
    text: str
    metadata: Dict[str, Any]
    score: float


class RetrievalResponse(BaseModel):
    items: List[RetrievedChunk]
    top_score: float

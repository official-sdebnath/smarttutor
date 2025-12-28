from pydantic import BaseModel
from typing import List, Dict, Any


class WebSearchRequest(BaseModel):
    query: str
    k: int = 5


class WebSearchResponse(BaseModel):
    answer: str
    items: List[Dict[str, Any]]
    top_score: float

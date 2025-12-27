import os
import requests

from shared.schemas.retrieval import RetrievalResponse

RETRIEVAL_SERVICE_URL = os.getenv(
    "RETRIEVAL_SERVICE_URL",
    "http://localhost:8001",
)

TIMEOUT = float(os.getenv("RETRIEVAL_TIMEOUT", "10"))


def retrieve_chunks(query: str, k: int = 5) -> RetrievalResponse:
    resp = requests.post(
        f"{RETRIEVAL_SERVICE_URL}/retrieve",
        json={"query": query, "k": k},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return RetrievalResponse(**resp.json())

import os
import requests
from shared.schemas.web_search import WebSearchResponse

WEB_SEARCH_SERVICE_URL = os.getenv(
    "WEB_SEARCH_SERVICE_URL",
    "http://web_search_service:8004",
)

TIMEOUT = float(os.getenv("WEB_SEARCH_TIMEOUT", "20"))


def search_web(query: str, k: int = 5):
    resp = requests.post(
        f"{WEB_SEARCH_SERVICE_URL}/search",
        json={"query": query, "k": k},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return WebSearchResponse(**resp.json())

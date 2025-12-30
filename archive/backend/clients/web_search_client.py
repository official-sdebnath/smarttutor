import os
import requests
from shared.schemas.web_search import WebSearchRequest, WebSearchResponse

WEB_SEARCH_SERVICE_URL = os.getenv(
    "WEB_SEARCH_SERVICE_URL",
    "http://localhost:8004",
)

TIMEOUT = float(os.getenv("WEB_SEARCH_TIMEOUT", "20"))


def search_web(query: str, k: int = 5) -> WebSearchResponse:
    """
    Calls the web search microservice.
    """
    payload = WebSearchRequest(query=query, k=k).dict()

    resp = requests.post(
        f"{WEB_SEARCH_SERVICE_URL}/search",
        json=payload,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()

    return WebSearchResponse(**resp.json())

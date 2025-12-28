import os
import requests
from shared.schemas.ingestion import IngestRequest, IngestResponse

INGESTION_SERVICE_URL = os.getenv(
    "INGESTION_SERVICE_URL",
    "http://localhost:8003",
)

TIMEOUT = float(os.getenv("INGESTION_TIMEOUT", "60"))


def ingest_directory(path: str) -> IngestResponse:
    """
    Calls the ingestion microservice to ingest documents from a directory.
    """
    payload = IngestRequest(path=path).dict()

    resp = requests.post(
        f"{INGESTION_SERVICE_URL}/ingest",
        json=payload,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()

    return IngestResponse(**resp.json())

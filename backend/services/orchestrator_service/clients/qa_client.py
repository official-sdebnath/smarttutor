import os
import requests
from shared.schemas.qa import QAResponse

QA_SERVICE_URL = os.getenv(
    "QA_SERVICE_URL",
    "http://qa_service:8002",
)

TIMEOUT = float(os.getenv("QA_TIMEOUT", "20"))


def ask_question(question: str, conversation_context: str | None = None, k: int = 5):
    resp = requests.post(
        f"{QA_SERVICE_URL}/ask",
        json={
            "question": question,
            "conversation_context": conversation_context,
            "k": k,
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return QAResponse(**resp.json())

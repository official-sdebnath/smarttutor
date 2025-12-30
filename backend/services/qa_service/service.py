from typing import Dict, Any, List

from qa_service.llm import llm
from qa_service.prompt import qa_prompt
from qa_service.config import RETRIEVAL_K_DEFAULT
from qa_service.retrieval_client import retrieve_chunks


def build_context(items: List[Dict[str, Any]]) -> str:
    parts = []
    for i, c in enumerate(items, start=1):
        meta = c.get("metadata", {}) or {}
        parts.append(
            f"[Chunk {i} | source={meta.get('source')} "
            f"page={meta.get('page')}]\n{c.get('text')}\n"
        )
    return "\n\n".join(parts)


def answer_question(
    question: str,
    conversation_context: str | None = None,
    k: int | None = None,
) -> Dict[str, Any]:
    """
    Full QA pipeline:
    1. Call retrieval microservice
    2. Build context
    3. Call LLM
    4. Return structured response
    """

    retrieval = retrieve_chunks(question, k or RETRIEVAL_K_DEFAULT)

    items = [item.dict() for item in retrieval.items]
    top_score = retrieval.top_score

    if not items:
        return {
            "answer": "I couldn't find anything relevant in the knowledge base.",
            "items": [],
            "top_score": 0.0,
        }

    context = build_context(items)

    prompt = qa_prompt.format(
        question=question,
        conversation=conversation_context or "None",
        context=context,
    )

    response = llm.invoke(prompt)

    return {
        "answer": response.content if hasattr(response, "content") else str(response),
        "items": items,
        "top_score": float(top_score),
    }

from typing import List, Dict, Any
from tavily import TavilyClient
from .llm import groq
from .prompt import prompt
from .config import TAVILY_API_KEY
from langchain_core.output_parsers import StrOutputParser


tavily = TavilyClient(api_key=TAVILY_API_KEY)

parser = StrOutputParser()

chain = prompt | groq | parser


def search_web(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Purpose: Search the web for relevant documents.

    Input: 1. query (str): The query to search for.
           2. k (int): The number of documents to return.

    Output: List[Dict[str, Any]]: A list of documents with their metadata and text.
    """
    try:
        resp = tavily.search(query=query, num_results=k)
        return resp.get("results", []) or []
    except Exception as e:
        print(f"Error searching web: {e}")
        return []


def normalize(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Purpose: Normalize raw tavily results.

    Input: 1. results (List[Dict[str, Any]]): A list of documents with their metadata and text.

    Output: List[Dict[str, Any]]: A list of documents with their metadata and text.
    """
    items = []
    for r in results:
        items.append(
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "content": (
                    r.get("content") or r.get("raw_content") or r.get("snippet") or ""
                )[:1500],
                "score": float(r.get("score", 0.0)),
            }
        )
    items.sort(key=lambda x: x["score"], reverse=True)
    return items


def synthesize_answer(question: str, items: List[Dict[str, Any]]) -> str:
    if not items:
        return "no answer found"

    evidence = ""
    for i, it in enumerate(items, start=1):
        evidence += (
            f"[{i}] title: {it['title']}\n"
            f"url: {it['url']}\n"
            f"content: {it['content']}\n\n"
        )

    try:
        answer = chain.invoke(
            {
                "question": question,
                "evidence": evidence,  # ✅ KEY FIX
            }
        )
        answer = answer.strip()
        return answer if answer else "no answer found"
    except Exception:
        return "no answer found"


def search_and_synthesize(query: str, k: int = 5) -> Dict[str, Any]:
    """
    Purpose: Search the web for relevant documents and synthesize an answer.

    Input: 1. query (str): The query to search for.
           2. k (int): The number of documents to return.

    Output: Dict[str, Any]: A dictionary containing the answer and the sources used.
    """
    raw = search_web(query, k=k)
    items = normalize(raw)
    answer = synthesize_answer(query, items)

    return {
        "type": "web",
        "items": items,
        "top_score": items[0]["score"] if items else 0.0,
        "answer": answer,
    }

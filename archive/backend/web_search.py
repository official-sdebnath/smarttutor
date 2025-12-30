import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=tavily_api_key)

groq_api_key = os.getenv("GROQ_API_KEY")
groq = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=groq_api_key,
    temperature=0,
    max_retries=2,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a web research assistant.\n"
                "Using the provided web excerpts, answer the user's question.\n"
                "You may summarize, combine, and rephrase information.\n"
                "If the information is insufficient, say so briefly."
            ),
        ),
        ("human", "Question:\n{question}\n\nWeb excerpts:\n{evidence}\n\nAnswer:"),
    ]
)

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

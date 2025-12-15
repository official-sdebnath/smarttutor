import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from backend.services.retrieval import search_chunks


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    temperature=0,
    max_retries=2,
)


def build_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Purpose: Build a context string from a list of chunks.

    Input: 1. chunks (List[Dict[str, Any]]): A list of chunks with their metadata and text.

    Output: str: A string containing the context.
    """
    parts = []
    for i, c in enumerate(chunks, start=1):
        meta = c.get("metadata", {})
        src = meta.get("source")
        page = meta.get("page")
        parts.append(f"[Chunk {i} | source={src}, page={page}]\n{c['text']}\n")
    return "\n\n".join(parts)


def retriever(question: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Purpose: Retrieve top-k chunks from MongoDB Atlas.

    Input: 1. question (str): The question to search for.
           2. k (int): The number of chunks to retrieve.

    Output: List[Dict[str, Any]]: A list of chunks with their metadata and text.
    """
    return search_chunks(question, k=k)


retriever = RunnableLambda(retriever)

context_builder = RunnableLambda(build_context)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are SmartTutor, a helpful AI tutor. "
            "Answer the user's question using ONLY the provided context. "
            "If the answer is not in the context, say you don't know.",
        ),
        (
            "human",
            "Context:\n{context}\n\nQuestion: {question}\nAnswer:",
        ),
    ]
)

parser = StrOutputParser()

chain = (
    {
        "context": retriever | context_builder,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | parser
)


def extract_sources_from_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Purpose: Extract sources from chunks.

    Input: chunks (List[Dict[str, Any]]): A list of chunks with their metadata and text.

    Output: List[Dict[str, Any]]: A list of sources with their page numbers and chunk indices.
    """
    items = []
    for c in chunks:
        meta = c.get("metadata", {}) or {}
        items.append(
            {
                "source": meta.get("source"),
                "page": meta.get("page"),
                "chunk_index": meta.get("chunk_index"),
                "snippet": (c.get("text") or c.get("text")[:500])
                if isinstance(c, dict)
                else (getattr(c, "page_content", "")[:500]),
                "score": float(c.get("score", 0.0)),
            }
        )
    # sort by score desc when available
    items.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return items


def answer_question(question: str, k: int = 5) -> Dict[str, Any]:
    """
    Purpose: Retrieve top-k chunks and generate an answer with OpenAI.
    Returns both answer and the sources used.

    Input: 1. question (str): The question to answer.
           2. k (int): The number of chunks to retrieve.

    Output: Dict[str, Any]: A dictionary containing the answer and the sources used.
    """
    chunks = search_chunks(question, k=k)
    items = extract_sources_from_chunks(chunks)
    top_score = items[0]["score"] if items else 0.0

    if not chunks:
        answer_text = "I couldn't find anything relevant in the knowledge base."
    else:
        answer_text = chain.invoke(question)

    return {
        "type": "rag",
        "items": items,
        "top_score": float(top_score),
        "answer": answer_text,
    }

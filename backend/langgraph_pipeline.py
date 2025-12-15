from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser

from backend.services.qa import answer_question
from backend.services.web_search import search_and_synthesize

from typing import Dict, Any, TypedDict, Optional
from models.models import EvalResult


# -------------------------
# Config
# -------------------------
RAG_THRESHOLD = 0.7
EVAL_THRESHOLD = 0.7

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)

eval_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}},
)


# -------------------------
# State
# -------------------------
class QAState(TypedDict):
    question: str  # User query

    rag_result: Optional[
        Dict[str, Any]
    ]  # Contains response strcuture from rag pipeline
    web_result: Optional[
        Dict[str, Any]
    ]  # Contains response strcuture from web pipeline

    final_answer: Optional[str]  # Contains final answer
    eval_score: Optional[float]  # Ranging from 0 to 1


# -------------------------
# Nodes
# -------------------------
def rag_node(state: QAState) -> QAState:
    """Purpose: Initialize node for using RAG agent"""
    result = answer_question(state["question"], k=5)
    return {**state, "rag_result": result}


def should_use_web(state: QAState) -> str:
    """Purpose: Determine whether to use the web pipeline or not."""
    rag = state.get("rag_result")
    if not rag:
        return "web"

    if rag["top_score"] >= RAG_THRESHOLD:
        return "evaluate"
    return "web"


def web_node(state: QAState) -> QAState:
    """Purpose: Initialize node for using web agent"""
    result = search_and_synthesize(state["question"], k=5)
    return {**state, "web_result": result}


# -------------------------
# Evaluator
# -------------------------
eval_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a strict evaluator.\n"
                "Evaluate the answer based on:\n"
                "- factual correctness\n"
                "- completeness\n"
                "- clarity\n\n"
                "{format_instructions}"
            ),
        ),
        (
            "human",
            "Question:\n{question}\n\nAnswer:\n{answer}\n\nEvidence:\n{evidence}",
        ),
    ]
)

parser = PydanticOutputParser(pydantic_object=EvalResult)
eval_chain = eval_prompt | eval_llm | parser


def evaluator_node(state: QAState) -> QAState:
    """Purpose: Initialize node for using evaluator agent"""
    candidate = (
        state["rag_result"]
        if state.get("rag_result") and state["rag_result"]["top_score"] >= RAG_THRESHOLD
        else state.get("web_result")
    )

    evidence = ""
    for i, it in enumerate(candidate["items"][:3], start=1):
        evidence += (
            f"[{i}] "
            f"title={it.get('title') or it.get('source')} | "
            f"score={it.get('score')}\n"
        )

    try:
        result: EvalResult = eval_chain.invoke(
            {
                "question": state["question"],
                "answer": candidate["answer"],
                "evidence": evidence,
                "format_instructions": parser.get_format_instructions(),
            }
        )
        score = result.score
    except Exception as e:
        print("Evaluator failed:", e)
        score = 0.0  # fail-safe

    return {
        **state,
        "final_answer": candidate["answer"],
        "eval_score": score,
    }


# -------------------------
# Rewrite Node
# -------------------------
rewrite_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Rewrite the answer to be clearer, more structured, and concise. Do not add new facts.",
        ),
        ("human", "Original answer:\n{answer}"),
    ]
)

rewrite_chain = rewrite_prompt | llm | StrOutputParser()


def rewrite_node(state: QAState) -> QAState:
    """Purpose: Initialize node for using rewrite agent"""
    rewritten = rewrite_chain.invoke({"answer": state["final_answer"]})
    return {**state, "final_answer": rewritten}


# -------------------------
# Graph
# -------------------------
graph = StateGraph(QAState)

graph.add_node("rag", rag_node)
graph.add_node("web", web_node)
graph.add_node("evaluate", evaluator_node)
graph.add_node("rewrite", rewrite_node)

graph.add_edge(START, "rag")

graph.add_conditional_edges(
    "rag",
    should_use_web,
    {
        "web": "web",
        "evaluate": "evaluate",
    },
)

graph.add_edge("web", "evaluate")

graph.add_conditional_edges(
    "evaluate",
    lambda s: "rewrite" if s["eval_score"] < EVAL_THRESHOLD else END,
    {
        "rewrite": "rewrite",
        END: END,
    },
)
graph.add_edge("rewrite", END)

app = graph.compile()

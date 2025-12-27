from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import interrupt
from langgraph.store.base import BaseStore

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from backend.clients.qa_client import ask_question

# from backend.services.qa import answer_question
from backend.services.web_search import search_and_synthesize

from typing import Dict, Any, Optional
from models.models import EvalResult

from backend.dspy_modules.signatures import EvaluatorModule, RewriteModule
import time

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

# DSPy modules initialized
evaluator = EvaluatorModule()
rewriter = RewriteModule()


# -------------------------
# State
# -------------------------
class QAState(MessagesState):
    rag_result: Optional[
        Dict[str, Any]
    ]  # Contains response strcuture from rag pipeline
    web_result: Optional[
        Dict[str, Any]
    ]  # Contains response strcuture from web pipeline
    final_answer: Optional[str]  # Contains final answer
    eval_score: Optional[float]  # Ranging from 0 to 1
    human_feedback: Optional[str]  # Contains human feedback
    memory_written: bool = False  # Whether memory has been written


# -------------------------- Helpers --------------------------


def last_user_message(state: QAState) -> str:
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            return m.content
    return ""


def conversation_context(state: QAState, max_turns: int = 6) -> str:
    """
    Build a compact conversational context for the LLM.
    """
    history = []
    for m in state["messages"][-max_turns:]:
        role = "User" if isinstance(m, HumanMessage) else "Assistant"
        history.append(f"{role}: {m.content}")
    return "\n".join(history)


def load_user_memory(store, user_id: str) -> str:
    namespace = ("memories", user_id)
    memories = store.search(namespace, query="")
    return "\n".join(m.value["data"] for m in memories)


def append_memory(store, user_id: str, text: str):
    store.put(
        ("memories", user_id),
        key=str(time.time()),
        value={"data": text},
    )


# -------------------------
# Nodes
# -------------------------
def rag_node(
    state: QAState,
    config: RunnableConfig,
    *,
    store: BaseStore,
) -> QAState:
    user_id = config["configurable"]["user_id"]

    memory = load_user_memory(store, user_id)
    context = conversation_context(state)

    augmented_context = f"""
    User memory:
    {memory}

    Conversation:
    {context}
    """

    qa_result = ask_question(
        question=last_user_message(state),
        conversation_context=augmented_context,
        k=5,
    )

    return {
        **state,
        "rag_result": {
            "answer": qa_result.answer,
            "items": qa_result.items,
            "top_score": qa_result.top_score,
        },
    }


def should_use_web(state: QAState) -> str:
    """Purpose: Determine whether to use the web pipeline or not."""
    rag = state.get("rag_result")
    if not rag:
        return "web"

    if rag["top_score"] >= RAG_THRESHOLD:
        return "evaluate"
    return "web"


def web_node(state: QAState) -> QAState:
    question = last_user_message(state)
    result = search_and_synthesize(question, k=5)
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


def evaluator_node(
    state: QAState,
    *,
    store: BaseStore,
    config: RunnableConfig,
) -> QAState:
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
        result = evaluator(
            question=last_user_message(state),
            answer=candidate["answer"],
            evidence=evidence,
        )
        score = float(result.score)
        user_id = config["configurable"]["user_id"]

        if score >= EVAL_THRESHOLD:
            append_memory(store, user_id, candidate["answer"])
            state["memory_written"] = True

    except Exception as e:
        print("DSPy evaluator failed:", e)
        score = 0.0

    return {
        **state,
        "final_answer": candidate["answer"],
        "eval_score": score,
        "messages": state["messages"] + [AIMessage(content=candidate["answer"])],
    }


# -------------------------
# Human Review Node
# -------------------------


def human_review_node(state: QAState) -> QAState:
    """
    Pause execution and ask human whether / how to rewrite.
    """
    feedback = interrupt(
        {
            "question": "Rewrite needed. Provide instructions or type 'approve'.",
            "current_answer": state["final_answer"],
        }
    )

    # feedback is what the human sends when resuming
    return {
        **state,
        "human_feedback": feedback,
    }


# -------------------------
# Rewrite Node
# -------------------------
rewrite_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Rewrite the answer based on human instructions. Do not add new facts.",
        ),
        (
            "human",
            "Original answer:\n{answer}\n\nHuman instructions:\n{instructions}",
        ),
    ]
)

rewrite_chain = rewrite_prompt | llm | StrOutputParser()


def rewrite_node(
    state: QAState,
    *,
    store: BaseStore,
    config: RunnableConfig,
) -> QAState:
    user_id = config["configurable"]["user_id"]
    feedback = state.get("human_feedback")

    # Case: human approves without rewrite
    if feedback is None or feedback.lower().strip() == "approve":
        if not state.get("memory_written"):
            append_memory(store, user_id, state["final_answer"])
            state["memory_written"] = True
        return state

    # Case: rewritten answer
    rewritten = rewriter(
        answer=state["final_answer"],
        rewrite_instructions=feedback,
    ).rewritten_answer

    append_memory(store, user_id, rewritten)
    state["memory_written"] = True

    return {
        **state,
        "final_answer": rewritten,
        "messages": state["messages"] + [AIMessage(content=rewritten)],
    }


# -------------------------
# Graph
# -------------------------
def build_graph(store, checkpointer):
    graph = StateGraph(QAState)

    graph.add_node("rag", rag_node)
    graph.add_node("web", web_node)
    graph.add_node("evaluate", evaluator_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("rewrite", rewrite_node)

    graph.add_edge(START, "rag")

    graph.add_conditional_edges(
        "rag",
        should_use_web,
        {"web": "web", "evaluate": "evaluate"},
    )

    graph.add_edge("web", "evaluate")

    graph.add_conditional_edges(
        "evaluate",
        lambda s: "human_review" if s["eval_score"] < EVAL_THRESHOLD else END,
        {"human_review": "human_review", END: END},
    )

    graph.add_edge("human_review", "rewrite")
    graph.add_edge("rewrite", END)

    return graph.compile(
        store=store,
        checkpointer=checkpointer,
    )

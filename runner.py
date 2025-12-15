from backend.langgraph_pipeline import app


def run_query(question: str):
    # Initial state must match QAState
    initial_state = {
        "question": question,
        "rag_result": None,
        "web_result": None,
        "final_answer": None,
        "eval_score": None,
    }

    result = app.invoke(initial_state)
    return result


if __name__ == "__main__":
    q = "what is diabetes?"
    output = run_query(q)

    print("\n===== FINAL ANSWER =====")
    print(output["final_answer"])

    print("\n===== DEBUG INFO =====")
    print("Eval score:", output["eval_score"])
    print("RAG used:", output["rag_result"] is not None)
    print("Web used:", output["web_result"] is not None)

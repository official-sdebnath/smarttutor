from backend.langgraph_pipeline import app


def chat():
    thread_id = "chat_1"  # SAME thread = persistent memory

    print("SmartTutor Chat (type 'exit' or 'quit' to stop)\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("👋 Exiting chat.")
            break

        initial_state = {
            "question": question,
            "rag_result": None,
            "web_result": None,
            "final_answer": None,
            "eval_score": None,
        }

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        # 🔹 Run the graph
        result = app.invoke(initial_state, config)

        print("\nAssistant:", result["final_answer"])
        print(f"(eval_score={result['eval_score']})")

        # 🔹 DEBUG: inspect persisted state
        state = app.get_state({"configurable": {"thread_id": thread_id}})
        print("\n[DEBUG] Current State Snapshot:")
        print(state.values)
        print("-" * 50)


if __name__ == "__main__":
    chat()

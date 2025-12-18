from backend.langgraph_pipeline import build_graph
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import HumanMessage
from langgraph.errors import GraphInterrupt

from dotenv import load_dotenv
import os
from urllib.parse import quote_plus 

load_dotenv()


user = os.getenv("SUPABASE_DB_USER")
password = quote_plus(os.getenv("SUPABASE_DB_PASSWORD"))  # 🔐 encoded in memory
host = os.getenv("SUPABASE_DB_HOST")
port = os.getenv("SUPABASE_DB_PORT", "5432")
db = os.getenv("SUPABASE_DB_NAME", "postgres")

SUPABASE_DB_URL = (
    f"postgresql://{user}:{password}@{host}:{port}/{db}"
)

def chat():
    thread_id = "chat_1"

    with (
        PostgresStore.from_conn_string(SUPABASE_DB_URL) as store,
        PostgresSaver.from_conn_string(SUPABASE_DB_URL) as checkpointer,
    ):
        app = build_graph(store, checkpointer)

        print("SmartTutor Chat (type 'exit' or 'quit' to stop)\n")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break

            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "user_id": "user_1",
                }
            }

            try:
                result = app.invoke(
                    {"messages": [HumanMessage(content=user_input)]},
                    config,
                )

            except GraphInterrupt:
                state = app.get_state(config)
                payload = state.tasks[0].interrupts[0].value
                print(payload["current_answer"])

                feedback = input("Rewrite or approve: ")
                result = app.invoke(
                    {"human_feedback": feedback},
                    config,
                )

            print("\nAssistant:", result["final_answer"])

if __name__ == "__main__":
    chat()

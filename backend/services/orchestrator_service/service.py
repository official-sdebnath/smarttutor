from orchestrator_service.langgraph_pipeline import build_graph
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import HumanMessage
from langgraph.errors import GraphInterrupt

from orchestrator_service.config import SUPABASE_DB_URL


class Orchestrator:
    def run(
        self,
        user_input: str,
        thread_id: str,
        user_id: str,
        human_feedback: str | None = None,
    ):
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id,
            }
        }

        # ✅ EXACTLY like runner.py
        with (
            PostgresStore.from_conn_string(SUPABASE_DB_URL) as store,
            PostgresSaver.from_conn_string(SUPABASE_DB_URL) as checkpointer,
        ):
            app = build_graph(store, checkpointer)

            if human_feedback:
                return app.invoke(
                    {"human_feedback": human_feedback},
                    config,
                )

            state = app.get_state(config)
            messages = state.values.get("messages", []) + [
                HumanMessage(content=user_input)
            ]

            try:
                return app.invoke(
                    {"messages": messages},
                    config,
                )

            except GraphInterrupt:
                state = app.get_state(config)
                interrupt_payload = state.tasks[0].interrupts[0].value
                return {
                    "needs_review": True,
                    "current_answer": interrupt_payload["current_answer"],
                }

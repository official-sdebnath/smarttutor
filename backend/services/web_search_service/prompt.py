from langchain_core.prompts import ChatPromptTemplate

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

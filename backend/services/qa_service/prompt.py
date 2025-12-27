from langchain_core.prompts import ChatPromptTemplate

qa_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are SmartTutor, a helpful AI tutor.\n"
            "Use the conversation context and retrieved documents to answer.\n"
            "If the answer is not supported by the context, say you don't know.",
        ),
        (
            "human",
            "Conversation so far:\n{conversation}\n\n"
            "Retrieved context:\n{context}\n\n"
            "Current question:\n{question}\n\nAnswer:",
        ),
    ]
)

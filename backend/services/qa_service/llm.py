from langchain_groq import ChatGroq
from backend.services.qa_service.config import GROQ_API_KEY

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0,
    max_retries=2,
)

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RETRIEVAL_K_DEFAULT = 5

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")

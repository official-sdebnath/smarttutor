import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
import dspy

load_dotenv()

user = os.getenv("SUPABASE_DB_USER")
password = quote_plus(os.getenv("SUPABASE_DB_PASSWORD"))
host = os.getenv("SUPABASE_DB_HOST")
port = os.getenv("SUPABASE_DB_PORT", "5432")
db = os.getenv("SUPABASE_DB_NAME", "postgres")

SUPABASE_DB_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

if not user or not password or not host:
    raise RuntimeError("Supabase DB env vars not set")


def configure_dspy():
    lm = dspy.LM(
        model="openai/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        api_base="https://api.groq.com/openai/v1",
        temperature=0,
    )

    dspy.configure(lm=lm)

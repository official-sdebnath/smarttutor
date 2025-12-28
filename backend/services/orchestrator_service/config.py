import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

user = os.getenv("SUPABASE_DB_USER")
password = quote_plus(os.getenv("SUPABASE_DB_PASSWORD"))
host = os.getenv("SUPABASE_DB_HOST")
port = os.getenv("SUPABASE_DB_PORT", "5432")
db = os.getenv("SUPABASE_DB_NAME", "postgres")

SUPABASE_DB_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

if not user or not password or not host:
    raise RuntimeError("Supabase DB env vars not set")

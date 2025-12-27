import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_ATLAS_URI")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

if not MONGODB_URI:
    raise RuntimeError("MONGODB_ATLAS_URI is not set")

if not EMBEDDING_MODEL:
    raise RuntimeError("EMBEDDING_MODEL is not set")

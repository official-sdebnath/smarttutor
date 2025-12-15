import os
from dotenv import load_dotenv
from utils.utils import get_mongodb_client

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_ATLAS_URI")
client = get_mongodb_client(MONGODB_URI)

db = client["smarttutor"]
chunks_collection = db["chunks"]

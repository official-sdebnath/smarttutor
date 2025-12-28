from pymongo import MongoClient
from pymongo.collection import Collection
from .config import MONGODB_URI

_client = MongoClient(MONGODB_URI)
_db = _client["smarttutor"]


def get_chunk_collection() -> Collection:
    """
    Purpose: Connects to MongoDB and returns a MongoClient object.
    Input: None
    Output: Collection: A Collection object.
    """
    return _db["chunks"]

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGODB_ATLAS_URI")


def get_mongodb_client(uri: str) -> MongoClient:
    """
    Connects to MongoDB and returns a MongoClient object.
    Input:
        uri (str): The URI of the MongoDB instance.

    Output:
        MongoClient: A MongoClient object.
    """
    try:
        return MongoClient(uri)
    except Exception as e:
        raise Exception("Unable to connect to MongoDB due to the following error: ", e)

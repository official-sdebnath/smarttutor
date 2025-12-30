from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings

from retrieval_service.db import get_chunk_collection
from retrieval_service.config import EMBEDDING_MODEL

_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def search_chunks(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Purpose: Embed the query and run a vector search in MongoDB Atlas.

    Input: 1. query (str): The query to search for.
           2. k (int): The number of chunks to return.

    Output: List[Dict[str, Any]]: A list of chunks with their metadata and score.
    """

    query_vec = _embeddings.embed_query(query)

    # Create a pipeline to search for the query in the chunks collection
    # The pipeline is a list of stages that are executed in order
    # The $vectorSearch stage is used to perform the vector search
    # The $project stage is used to project the fields to be returned
    pipeline = [
        {
            "$vectorSearch": {
                "index": "smarttutor_chunks_index",  # The Vector Search index name configured in Atlas
                "path": "embedding",  # The field name in the document that contains the embedding vector
                "queryVector": query_vec,
                "numCandidates": 100,  # The number of documents to consider before ranking and returning for the search
                "limit": k,  # The number of documents to return
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the _id field from the output
                "text": 1,  # Include the text field in the output
                "metadata": 1,  # Include the metadata field in the output
                "score": {
                    "$meta": "vectorSearchScore"
                },  # Include the score field in the output
            }
        },
    ]

    results = list(get_chunk_collection().aggregate(pipeline))
    return results

import os
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from backend.core.db import get_mongodb_client

from backend.core.db import chunks_collection

load_dotenv()

client = get_mongodb_client(os.getenv("MONGODB_ATLAS_URI"))


def load_documents(file_path: str) -> list:
    """
    Purpose:
        Load documents from a directory or a single file path
    Input:
        file_path (str): Takes a directory path or a single file path

    Returns:
        list: List of documents
    """
    p = Path(file_path)
    if p.is_dir():
        docs = []
        for pdf_file in p.glob("*.pdf"):
            loader = PyPDFLoader(str(pdf_file))
            docs.extend(loader.load())
        return docs
    else:
        raise ValueError("Unsupported file type")


def split_documents(docs: list) -> list[Document]:
    """
    Purpose: Splits documents into chunks

    Input:
        docs (list): List of documents

    Returns:
        list: List of split documents
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=128,
        length_function=len,
        is_separator_regex=False,
    )

    all_chunks = []
    for doc_index, doc in enumerate(docs):
        chunks = splitter.split_documents([doc])
        for chunk_index, chunk in enumerate(chunks):
            chunk.metadata["doc_index"] = doc_index
            chunk.metadata["chunk_index"] = chunk_index
            all_chunks.append(chunk)

    return all_chunks


def ingest_chunks(chunks: list[Document]) -> int:
    """
    Purpose: Ingests documents to MongoDB
    Input:
        chunks (list): List of split documents
    Returns:
        int: Number of documents ingested
    """
    # 0) Extract which sources are in this batch
    sources_in_batch = {c.metadata["source"] for c in chunks}

    # 1) Ask Mongo which of these sources already exist
    existing_sources = set(
        chunks_collection.distinct(
            "metadata.source",
            {"metadata.source": {"$in": list(sources_in_batch)}},
        )
    )

    # 2) Filter chunks to only *new* sources
    if existing_sources:
        print(f"Skipping already ingested sources: {existing_sources}")
        chunks = [c for c in chunks if c.metadata["source"] not in existing_sources]

    if not chunks:
        print("No new chunks to ingest (all sources already ingested).")
        return 0

    # 3) Build embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    texts = [c.page_content for c in chunks]
    vectors = embeddings.embed_documents(texts)

    # 4) Build Mongo records
    records = []
    for doc, vec in zip(chunks, vectors):
        records.append(
            {
                "text": doc.page_content,
                "metadata": doc.metadata,
                "embedding": vec,
            }
        )

    # 5) Insert only new ones
    res = chunks_collection.insert_many(records)
    inserted = len(res.inserted_ids)
    print(f"Inserted {inserted} docs into MongoDB Atlas.")
    return inserted


def full_ingest_from_dir(path: str) -> int:
    """
    Purpose: Ingests documents to MongoDB
    Input:
        path (str): Path to directory containing documents
    Returns:
        int: Number of documents ingested
    """
    docs = load_documents(path)
    chunks = split_documents(docs)
    return ingest_chunks(chunks)
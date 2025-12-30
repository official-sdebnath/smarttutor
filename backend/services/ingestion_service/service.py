from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from ingestion_service.config import EMBEDDING_MODEL
from ingestion_service.db import get_chunk_collection


def load_documents(dir_path: str) -> List[Document]:
    p = Path(dir_path)
    if not p.is_dir():
        raise ValueError("Path must be a directory")

    docs = []
    for pdf_file in p.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        docs.extend(loader.load())
    return docs


def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=128,
    )

    chunks = []
    for doc_index, doc in enumerate(docs):
        split = splitter.split_documents([doc])
        for chunk_index, chunk in enumerate(split):
            chunk.metadata["doc_index"] = doc_index
            chunk.metadata["chunk_index"] = chunk_index
            chunks.append(chunk)
    return chunks


def ingest_directory(path: str) -> int:
    docs = load_documents(path)
    chunks = split_documents(docs)

    collection = get_chunk_collection()

    # Dedup by source
    sources = {c.metadata["source"] for c in chunks}
    existing = set(
        collection.distinct(
            "metadata.source",
            {"metadata.source": {"$in": list(sources)}},
        )
    )

    chunks = [c for c in chunks if c.metadata["source"] not in existing]
    if not chunks:
        return 0

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    texts = [c.page_content for c in chunks]
    vectors = embeddings.embed_documents(texts)

    records = []
    for chunk, vec in zip(chunks, vectors):
        records.append(
            {
                "text": chunk.page_content,
                "metadata": chunk.metadata,
                "embedding": vec,
            }
        )

    res = collection.insert_many(records)
    return len(res.inserted_ids)

from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.ingestion import full_ingest_from_dir

router = APIRouter(prefix="/ingest", tags=["ingestion"])


class IngestRequest(BaseModel):
    path: str = "./docs/"   # default if you like


class IngestResponse(BaseModel):
    ingested_chunks: int


@router.post("", response_model=IngestResponse)
def ingest_docs(body: IngestRequest):
    inserted = full_ingest_from_dir(body.path)
    return IngestResponse(ingested_chunks=inserted)

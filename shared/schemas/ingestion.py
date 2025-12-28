from pydantic import BaseModel


class IngestRequest(BaseModel):
    path: str


class IngestResponse(BaseModel):
    ingested_chunks: int

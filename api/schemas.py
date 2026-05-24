from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["What should I check when a compressor bearing alarm occurs?"])
    top_k: int = Field(4, ge=1, le=8)


class Citation(BaseModel):
    source: str
    section: str
    page: str
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    confidence: str
    maintenance_actions: list[str]
    citations: list[Citation]
    retrieved_context: list[dict[str, object]]
    mode: str
    llm_provider: str


class HealthResponse(BaseModel):
    status: str
    mode: str
    llm_provider: str
    embedding_model: str
    chat_model: str
    document_count: int
    chunk_count: int
    vector_store_path: str
    document_source_path: str


class IngestResponse(BaseModel):
    status: str
    document_count: int
    chunk_count: int
    index_path: str
    indexed_at: str

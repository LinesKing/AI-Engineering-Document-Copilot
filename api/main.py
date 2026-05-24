from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, FastAPI

from api.schemas import AskRequest, AskResponse, HealthResponse, IngestResponse
from src.services import DocumentCopilotService


app = FastAPI(
    title="AI Engineering Document Copilot API",
    description="Production-style RAG API for engineering manuals and maintenance documents.",
    version="0.1.0",
)


@lru_cache(maxsize=1)
def get_service() -> DocumentCopilotService:
    service = DocumentCopilotService()
    service.ensure_demo_ready()
    return service


@app.get("/health", response_model=HealthResponse)
def health(service: DocumentCopilotService = Depends(get_service)) -> dict[str, object]:
    return service.health()


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, service: DocumentCopilotService = Depends(get_service)) -> dict[str, object]:
    return service.ask(question=request.question, top_k=request.top_k)


@app.post("/ingest", response_model=IngestResponse)
def ingest() -> dict[str, object]:
    get_service.cache_clear()
    service = get_service()
    return service.ingest()


@app.get("/documents")
def documents(service: DocumentCopilotService = Depends(get_service)) -> dict[str, object]:
    return service.list_documents()

from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app, get_service
from src.config import AppSettings
from src.documents.demo import create_demo_documents
from src.services import DocumentCopilotService


def test_api_health_and_ask(tmp_path) -> None:
    settings = AppSettings(
        copilot_mode="api",
        api_base_url="http://localhost:8000",
        llm_provider="demo",
        openai_api_key=None,
        embedding_model="local-tfidf",
        chat_model="demo-grounded-extractor",
        vector_store_path=tmp_path / "index",
        document_source_path=tmp_path / "manuals",
        runtime_path=tmp_path / "runtime",
    )
    create_demo_documents(settings.document_source_path)
    service = DocumentCopilotService(settings)
    service.ingest()

    app.dependency_overrides.clear()
    get_service.cache_clear()
    app.dependency_overrides[get_service] = lambda: service

    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    answer = client.post("/ask", json={"question": "How should I respond to cavitation symptoms?", "top_k": 3})
    assert answer.status_code == 200
    assert answer.json()["citations"]

    app.dependency_overrides.clear()

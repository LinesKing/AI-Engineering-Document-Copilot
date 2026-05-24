from __future__ import annotations

from src.config import AppSettings
from src.documents.demo import create_demo_documents
from src.services import DocumentCopilotService


def _settings(tmp_path) -> AppSettings:
    return AppSettings(
        copilot_mode="direct",
        api_base_url="http://localhost:8000",
        llm_provider="demo",
        openai_api_key=None,
        embedding_model="local-tfidf",
        chat_model="demo-grounded-extractor",
        vector_store_path=tmp_path / "index",
        document_source_path=tmp_path / "manuals",
        runtime_path=tmp_path / "runtime",
    )


def test_service_answers_with_citations(tmp_path) -> None:
    settings = _settings(tmp_path)
    create_demo_documents(settings.document_source_path)
    service = DocumentCopilotService(settings)
    service.ingest()

    result = service.ask("What should I do when compressor bearing temperature is high?")

    assert result["answer"]
    assert result["citations"]
    assert result["confidence"] in {"HIGH", "MEDIUM", "LOW"}
    assert result["citations"][0]["source"] == "compressor_maintenance_manual.md"

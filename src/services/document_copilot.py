from __future__ import annotations

from datetime import datetime, timezone

from src.config import AppSettings, get_settings
from src.documents.demo import create_demo_documents
from src.documents.loader import load_documents
from src.llm import build_llm_provider
from src.retrieval import TfidfVectorIndex


class DocumentCopilotService:
    def __init__(self, settings: AppSettings | None = None) -> None:
        self.settings = settings or get_settings()
        self._index: TfidfVectorIndex | None = None

    def ensure_demo_ready(self) -> None:
        has_manuals = self.settings.document_source_path.exists() and any(
            path.is_file() and path.stat().st_size > 0
            for path in self.settings.document_source_path.glob("*")
        )
        if not has_manuals:
            create_demo_documents(self.settings.document_source_path)
        if not TfidfVectorIndex.exists(self.settings.vector_store_path):
            self.ingest()

    def ingest(self) -> dict[str, object]:
        chunks = load_documents(self.settings.document_source_path)
        if not chunks:
            raise ValueError(f"No supported documents found in {self.settings.document_source_path}")
        index = TfidfVectorIndex.build(chunks)
        index_path = index.save(self.settings.vector_store_path)
        self._index = index
        return {
            "status": "indexed",
            "document_count": len(index.document_names()),
            "chunk_count": len(chunks),
            "index_path": str(index_path),
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _get_index(self) -> TfidfVectorIndex:
        if self._index is not None:
            return self._index
        if not TfidfVectorIndex.exists(self.settings.vector_store_path):
            self.ensure_demo_ready()
        self._index = TfidfVectorIndex.load(self.settings.vector_store_path)
        return self._index

    def ask(self, question: str, top_k: int = 4) -> dict[str, object]:
        index = self._get_index()
        results = index.search(question, top_k=top_k)
        llm = build_llm_provider(self.settings)
        answer_payload = llm.answer(question, results)
        return {
            "question": question,
            "answer": answer_payload["answer"],
            "confidence": answer_payload["confidence"],
            "maintenance_actions": answer_payload["maintenance_actions"],
            "citations": [
                {
                    "source": result.chunk.source,
                    "section": result.chunk.section,
                    "page": result.chunk.page,
                    "score": round(result.score, 4),
                }
                for result in results
            ],
            "retrieved_context": [result.to_dict() for result in results],
            "mode": self.settings.copilot_mode,
            "llm_provider": self.settings.llm_provider,
        }

    def health(self) -> dict[str, object]:
        index_exists = TfidfVectorIndex.exists(self.settings.vector_store_path)
        document_count = 0
        chunk_count = 0
        if index_exists:
            index = self._get_index()
            document_count = len(index.document_names())
            chunk_count = len(index.chunks)
        return {
            "status": "ok" if index_exists else "needs_index",
            "mode": self.settings.copilot_mode,
            "llm_provider": self.settings.llm_provider,
            "embedding_model": self.settings.embedding_model,
            "chat_model": self.settings.chat_model,
            "document_count": document_count,
            "chunk_count": chunk_count,
            "vector_store_path": str(self.settings.vector_store_path),
            "document_source_path": str(self.settings.document_source_path),
        }

    def list_documents(self) -> dict[str, object]:
        index = self._get_index()
        return {"documents": index.document_names(), "document_count": len(index.document_names())}

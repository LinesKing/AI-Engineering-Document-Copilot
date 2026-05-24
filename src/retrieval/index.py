from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.documents.models import DocumentChunk


INDEX_FILE = "engineering_manual_index.joblib"


@dataclass(frozen=True)
class RetrievalResult:
    chunk: DocumentChunk
    score: float

    def to_dict(self) -> dict[str, object]:
        payload = self.chunk.to_dict()
        payload["score"] = round(self.score, 4)
        return payload


class TfidfVectorIndex:
    def __init__(self, chunks: list[DocumentChunk], vectorizer: TfidfVectorizer, matrix) -> None:
        self.chunks = chunks
        self.vectorizer = vectorizer
        self.matrix = matrix

    @classmethod
    def build(cls, chunks: list[DocumentChunk]) -> "TfidfVectorIndex":
        if not chunks:
            raise ValueError("Cannot build an index without document chunks.")
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
        matrix = vectorizer.fit_transform([chunk.text for chunk in chunks])
        return cls(chunks=chunks, vectorizer=vectorizer, matrix=matrix)

    @classmethod
    def load(cls, vector_store_path: Path) -> "TfidfVectorIndex":
        payload = joblib.load(vector_store_path / INDEX_FILE)
        chunks = [DocumentChunk.from_dict(item) for item in payload["chunks"]]
        return cls(chunks=chunks, vectorizer=payload["vectorizer"], matrix=payload["matrix"])

    def save(self, vector_store_path: Path) -> Path:
        vector_store_path.mkdir(parents=True, exist_ok=True)
        index_path = vector_store_path / INDEX_FILE
        joblib.dump(
            {
                "chunks": [chunk.to_dict() for chunk in self.chunks],
                "vectorizer": self.vectorizer,
                "matrix": self.matrix,
            },
            index_path,
        )
        return index_path

    @staticmethod
    def exists(vector_store_path: Path) -> bool:
        index_path = vector_store_path / INDEX_FILE
        return index_path.exists() and index_path.stat().st_size > 0

    def search(self, query: str, top_k: int = 4) -> list[RetrievalResult]:
        if not query.strip():
            return []
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).flatten()
        ranked_indexes = scores.argsort()[::-1][:top_k]
        return [
            RetrievalResult(chunk=self.chunks[index], score=float(scores[index]))
            for index in ranked_indexes
            if scores[index] > 0
        ]

    def document_names(self) -> list[str]:
        return sorted({chunk.source for chunk in self.chunks})

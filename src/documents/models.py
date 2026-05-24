from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    source: str
    section: str
    page: str
    equipment_type: str
    maintenance_category: str

    def to_dict(self) -> dict[str, str]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "source": self.source,
            "section": self.section,
            "page": self.page,
            "equipment_type": self.equipment_type,
            "maintenance_category": self.maintenance_category,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, str]) -> "DocumentChunk":
        return cls(**payload)

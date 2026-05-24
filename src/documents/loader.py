from __future__ import annotations

import hashlib
import re
from pathlib import Path

from src.documents.models import DocumentChunk


SUPPORTED_EXTENSIONS = {".md", ".txt"}


def _infer_equipment_type(path: Path, text: str) -> str:
    haystack = f"{path.stem} {text}".lower()
    for label in ("compressor", "pump", "conveyor", "motor", "valve"):
        if label in haystack:
            return label.title()
    return "General Equipment"


def _infer_category(section: str, text: str) -> str:
    haystack = f"{section} {text}".lower()
    categories = {
        "Safety": ("safety", "isolation", "lockout", "emergency"),
        "Troubleshooting": ("alarm", "trip", "symptom", "cavitation", "tracking"),
        "Preventive Maintenance": ("weekly", "inspection", "preventive", "check"),
        "Overhaul": ("overhaul", "alignment", "restart", "acceptance"),
        "Lubrication": ("oil", "lubrication", "filter"),
    }
    for category, keywords in categories.items():
        if any(keyword in haystack for keyword in keywords):
            return category
    return "Maintenance"


def _split_sections(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^#{1,3}\s+(.+)$", text))
    if not matches:
        return [("General", text.strip())]

    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title = match.group(1).strip()
        body = text[start:end].strip()
        if body:
            sections.append((title, body))
    return sections


def chunk_text(text: str, max_words: int = 120, overlap_words: int = 24) -> list[str]:
    words = text.split()
    if not words:
        return []
    if len(words) <= max_words:
        return [" ".join(words)]

    chunks: list[str] = []
    step = max(1, max_words - overlap_words)
    for start in range(0, len(words), step):
        chunk_words = words[start : start + max_words]
        if chunk_words:
            chunks.append(" ".join(chunk_words))
        if start + max_words >= len(words):
            break
    return chunks


def load_documents(document_dir: Path) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in sorted(document_dir.glob("*")):
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        equipment_type = _infer_equipment_type(path, text)
        for section_index, (section, body) in enumerate(_split_sections(text), start=1):
            for chunk_index, chunk in enumerate(chunk_text(body), start=1):
                digest = hashlib.sha1(f"{path.name}:{section}:{chunk_index}:{chunk}".encode("utf-8")).hexdigest()[:12]
                chunks.append(
                    DocumentChunk(
                        chunk_id=digest,
                        text=chunk,
                        source=path.name,
                        section=section,
                        page=f"S{section_index}",
                        equipment_type=equipment_type,
                        maintenance_category=_infer_category(section, chunk),
                    )
                )
    return chunks

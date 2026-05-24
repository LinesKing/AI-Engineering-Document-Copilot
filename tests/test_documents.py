from __future__ import annotations

from src.documents.loader import chunk_text, load_documents


def test_chunk_text_preserves_content() -> None:
    chunks = chunk_text(" ".join(f"word{i}" for i in range(40)), max_words=20, overlap_words=5)
    assert len(chunks) == 3
    assert chunks[0].startswith("word0")
    assert "word15" in chunks[1]


def test_load_documents_preserves_metadata(tmp_path) -> None:
    manual = tmp_path / "pump_manual.md"
    manual.write_text("# Pump Manual\n\n## Seal Leakage\nInspect seal flush pressure.", encoding="utf-8")
    chunks = load_documents(tmp_path)
    assert chunks[0].source == "pump_manual.md"
    assert chunks[0].section == "Seal Leakage"
    assert chunks[0].equipment_type == "Pump"

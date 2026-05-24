from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCUMENT_SOURCE_PATH = PROJECT_ROOT / "docs" / "sample_manuals"
DEFAULT_VECTOR_STORE_PATH = PROJECT_ROOT / "indexes" / "vector_store"
DEFAULT_RUNTIME_PATH = PROJECT_ROOT / "data" / "runtime"

VALID_COPILOT_MODES = {"api", "direct"}
VALID_LLM_PROVIDERS = {"demo", "openai"}


def normalize_copilot_mode(value: str | None) -> str:
    mode = (value or "api").strip().lower()
    if mode not in VALID_COPILOT_MODES:
        valid = ", ".join(sorted(VALID_COPILOT_MODES))
        raise ValueError(f"COPILOT_MODE must be one of: {valid}")
    return mode


def normalize_llm_provider(value: str | None) -> str:
    provider = (value or "demo").strip().lower()
    if provider not in VALID_LLM_PROVIDERS:
        valid = ", ".join(sorted(VALID_LLM_PROVIDERS))
        raise ValueError(f"LLM_PROVIDER must be one of: {valid}")
    return provider


def get_app_setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st

        secret_value = st.secrets.get(name, default)
        return str(secret_value) if secret_value is not None else default
    except Exception:
        return default


@dataclass(frozen=True)
class AppSettings:
    copilot_mode: str
    api_base_url: str
    llm_provider: str
    openai_api_key: str | None
    embedding_model: str
    chat_model: str
    vector_store_path: Path
    document_source_path: Path
    runtime_path: Path


def get_settings() -> AppSettings:
    return AppSettings(
        copilot_mode=normalize_copilot_mode(get_app_setting("COPILOT_MODE", "api")),
        api_base_url=get_app_setting("API_BASE_URL", "http://localhost:8000") or "http://localhost:8000",
        llm_provider=normalize_llm_provider(get_app_setting("LLM_PROVIDER", "demo")),
        openai_api_key=get_app_setting("OPENAI_API_KEY"),
        embedding_model=get_app_setting("EMBEDDING_MODEL", "local-tfidf") or "local-tfidf",
        chat_model=get_app_setting("CHAT_MODEL", "demo-grounded-extractor") or "demo-grounded-extractor",
        vector_store_path=Path(get_app_setting("VECTOR_STORE_PATH", str(DEFAULT_VECTOR_STORE_PATH)) or DEFAULT_VECTOR_STORE_PATH),
        document_source_path=Path(get_app_setting("DOCUMENT_SOURCE_PATH", str(DEFAULT_DOCUMENT_SOURCE_PATH)) or DEFAULT_DOCUMENT_SOURCE_PATH),
        runtime_path=Path(get_app_setting("RUNTIME_PATH", str(DEFAULT_RUNTIME_PATH)) or DEFAULT_RUNTIME_PATH),
    )

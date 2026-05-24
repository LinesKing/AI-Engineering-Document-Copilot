from __future__ import annotations

import pytest

from src.config import normalize_copilot_mode, normalize_llm_provider


def test_normalize_copilot_mode_defaults_to_api() -> None:
    assert normalize_copilot_mode(None) == "api"


def test_normalize_copilot_mode_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        normalize_copilot_mode("not-real")


def test_normalize_llm_provider_defaults_to_demo() -> None:
    assert normalize_llm_provider(None) == "demo"

"""Utilidades compartidas por los tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from scraper.config import Settings
from scraper.engines.llm_engine import ollama_available
from scraper.spec import load_spec

FIXTURES = Path(__file__).parent / "fixtures"


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.fixture
def books_v1() -> str:
    return read_fixture("books_v1.html")


@pytest.fixture
def books_v2() -> str:
    return read_fixture("books_v2_redesign.html")


@pytest.fixture
def books_spec():
    return load_spec(FIXTURES / "books_spec.yaml")


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Ajustes aislados: estado en tmp y sin esperas reales."""
    return Settings(
        state_dir=tmp_path / "state",
        rate_limit_seconds=0.0,
        max_retries=1,
        backoff_factor=0.0,
        respect_robots=True,
        adaptive=True,
    )


@pytest.fixture
def llm_settings(tmp_path: Path) -> Settings:
    return Settings(state_dir=tmp_path / "state", rate_limit_seconds=0.0, llm_timeout=120.0)


def pytest_collection_modifyitems(config, items):
    """Los tests marcados ``llm`` se saltan solos si no hay modelo disponible."""
    base_url = Settings().llm_base_url
    if ollama_available(base_url, timeout=2.0):
        return
    skip = pytest.mark.skip(reason=f"Ollama no responde en {base_url}; test LLM omitido")
    for item in items:
        if "llm" in item.keywords:
            item.add_marker(skip)

"""Paginación: seguir el enlace 'siguiente' hasta el máximo de páginas."""

from __future__ import annotations

from urllib.parse import urljoin

import pytest

from scraper.engines.scrapling_engine import ScraplingEngine
from scraper.spec import load_spec

from conftest import FIXTURES, read_fixture

BASE = "https://books.toscrape.com/"
PAGES = {
    BASE: "books_v1.html",
    urljoin(BASE, "catalogue/page-2.html"): "books_page2.html",
    urljoin(BASE, "catalogue/page-3.html"): "books_page3.html",
}


class FakePagedEngine(ScraplingEngine):
    """Sirve las páginas desde fixtures en vez de la red, sin tocar la paginación."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requested: list[str] = []

    def _fetch(self, url: str):  # type: ignore[override]
        self.requested.append(url)
        if url not in PAGES:
            raise AssertionError(f"URL inesperada: {url}")
        return self.parse_html(read_fixture(PAGES[url]), url)


@pytest.fixture
def spec():
    return load_spec(FIXTURES / "books_spec.yaml")


def test_recorre_las_tres_paginas(settings, spec):
    engine = FakePagedEngine(settings=settings)
    result = engine.scrape(BASE, spec)

    assert result.ok, result.errors
    assert engine.requested == list(PAGES)
    assert result.meta["pages"] == 3
    assert len(result.data) == 6  # 3 + 2 + 1
    assert result.data[0]["titulo"] == "A Light in the Attic"
    assert result.data[3]["titulo"] == "Sharp Objects"
    assert result.data[5]["titulo"] == "The Black Maria"


def test_respeta_el_maximo_de_paginas(settings, spec):
    spec.pagination.max_pages = 2
    engine = FakePagedEngine(settings=settings)
    result = engine.scrape(BASE, spec)

    assert len(engine.requested) == 2
    assert result.meta["pages"] == 2
    assert len(result.data) == 5


def test_sin_paginacion_solo_la_primera(settings, spec):
    spec.pagination = None
    engine = FakePagedEngine(settings=settings)
    result = engine.scrape(BASE, spec)

    assert engine.requested == [BASE]
    assert len(result.data) == 3


def test_para_cuando_se_acaban_los_enlaces(settings, spec):
    """La página 3 no tiene 'siguiente': debe parar aunque max_pages sea mayor."""
    spec.pagination.max_pages = 10
    engine = FakePagedEngine(settings=settings)
    result = engine.scrape(BASE, spec)

    assert result.meta["pages"] == 3
    assert len(result.data) == 6


def test_el_enlace_relativo_se_resuelve_contra_la_pagina(settings, spec):
    engine = FakePagedEngine(settings=settings)
    engine.scrape(BASE, spec)
    assert engine.requested[1] == "https://books.toscrape.com/catalogue/page-2.html"

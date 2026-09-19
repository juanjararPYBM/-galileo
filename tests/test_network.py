"""Integración real contra sitios públicos hechos para practicar scraping.

Se ejecutan con ``pytest -m network``. Quedan fuera de la corrida por defecto.
"""

from __future__ import annotations

import pytest

from scraper.engines.scrapling_engine import ScraplingEngine
from scraper.spec import parse_spec

pytestmark = pytest.mark.network

QUOTES = "https://quotes.toscrape.com/"
BOOKS = "https://books.toscrape.com/"


def _alcanzable(url: str, timeout: float = 15.0) -> bool:
    """¿Se puede salir a ese host? (en entornos con egress restringido, no)."""
    try:
        from urllib.request import Request, urlopen

        with urlopen(Request(url, method="HEAD"), timeout=timeout) as response:  # noqa: S310
            return response.status < 400
    except Exception:  # noqa: BLE001
        return False


@pytest.fixture(autouse=True)
def _requiere_salida_a_internet():
    """Marca como omitidos, no fallidos, los tests si la red bloquea estos sitios."""
    if not _alcanzable(BOOKS):
        pytest.skip(f"Sin salida a {BOOKS} (red restringida); test de integración omitido")


@pytest.fixture
def quotes_spec():
    return parse_spec(
        {
            "name": "quotes",
            "item_selector": "div.quote",
            "fields": {
                "cita": "span.text::text",
                "autor": "small.author::text",
                "etiquetas": {"selector": "div.tags a.tag::text", "many": True},
            },
            "pagination": {"next_selector": "li.next a::attr(href)", "max_pages": 2},
        }
    )


@pytest.fixture
def books_spec_net():
    return parse_spec(
        {
            "name": "books_net",
            "item_selector": "article.product_pod",
            "fields": {
                "titulo": "h3 a::attr(title)",
                "precio": "p.price_color::text",
                "disponibilidad": "p.instock.availability::text",
            },
            "pagination": {"next_selector": "li.next a::attr(href)", "max_pages": 2},
        }
    )


def test_quotes_toscrape(settings, quotes_spec):
    result = ScraplingEngine(settings=settings).scrape(QUOTES, quotes_spec)

    assert result.ok, result.errors
    assert result.meta["pages"] == 2
    assert len(result.data) == 20  # 10 citas por página
    primera = result.data[0]
    assert primera["autor"] == "Albert Einstein"
    assert primera["cita"].startswith("“The world as we have created it")
    assert "change" in primera["etiquetas"]


def test_books_toscrape_tres_paginas(settings, books_spec_net):
    books_spec_net.pagination.max_pages = 3
    result = ScraplingEngine(settings=settings).scrape(BOOKS, books_spec_net)

    assert result.ok, result.errors
    assert result.meta["pages"] == 3
    assert len(result.data) == 60  # 20 libros por página
    assert result.data[0]["titulo"] == "A Light in the Attic"
    assert result.data[0]["precio"].endswith("51.77")
    assert all(fila["titulo"] and fila["precio"] for fila in result.data)


def test_robots_se_consulta_de_verdad(settings):
    """robots.txt real de books.toscrape.com: debe leerse y permitir el catálogo."""
    from scraper.politeness import RobotsPolicy, robots_url_for

    policy = RobotsPolicy(settings.user_agent, timeout=20.0)
    assert policy._parser_for(BOOKS) is not None, f"no se pudo leer {robots_url_for(BOOKS)}"
    assert policy.can_fetch(BOOKS) is True


def test_modo_dynamic_con_navegador(settings, books_spec_net):
    """Comprueba que el modo con navegador (Playwright) también funciona."""
    books_spec_net.pagination = None
    result = ScraplingEngine(settings=settings, mode="dynamic").scrape(BOOKS, books_spec_net)

    assert result.ok, result.errors
    assert len(result.data) == 20
    assert result.data[0]["titulo"] == "A Light in the Attic"

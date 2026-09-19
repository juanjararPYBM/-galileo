"""Extracción por selectores con HTML fijo (sin red)."""

from __future__ import annotations

import pytest

from scraper.engines.scrapling_engine import ScraplingEngine
from scraper.spec import parse_spec

URL = "https://books.toscrape.com/"

TITULOS = ["A Light in the Attic", "Tipping the Velvet", "Soumission"]
PRECIOS = ["£51.77", "£53.74", "£50.10"]
STOCK = ["In stock", "In stock", "Out of stock"]


def test_extrae_items_y_campos(settings, books_spec, books_v1):
    engine = ScraplingEngine(settings=settings)
    result = engine.scrape_html(books_v1, URL, books_spec)

    assert result.ok, result.errors
    assert result.engine == "scrapling"
    assert len(result.data) == 3
    assert [r["titulo"] for r in result.data] == TITULOS
    assert [r["precio"] for r in result.data] == PRECIOS
    assert [r["disponibilidad"] for r in result.data] == STOCK
    assert result.data[0]["enlace"].endswith("a-light-in-the-attic_1000/index.html")


def test_resultado_tiene_metadatos_y_duracion(settings, books_spec, books_v1):
    result = ScraplingEngine(settings=settings).scrape_html(books_v1, URL, books_spec)
    assert result.duration_s >= 0
    assert result.meta["items"] == 3
    assert result.timestamp.tzinfo is not None
    assert result.to_dict()["engine"] == "scrapling"


def test_sin_item_selector_devuelve_un_solo_registro(settings, books_v1):
    spec = parse_spec(
        {
            "name": "pagina",
            "fields": {
                "titulos": {"selector": "article.product_pod h3 a::attr(title)", "many": True},
                "primer_precio": ".price_color::text",
            },
        }
    )
    result = ScraplingEngine(settings=settings).scrape_html(books_v1, URL, spec)
    assert len(result.data) == 1
    assert result.data[0]["titulos"] == TITULOS
    assert result.data[0]["primer_precio"] == "£51.77"


def test_campo_sin_coincidencias_usa_default(settings, books_v1):
    spec = parse_spec(
        {
            "name": "x",
            "item_selector": "article.product_pod",
            "fields": {
                "titulo": "h3 a::attr(title)",
                "isbn": {"selector": ".no-existe::text", "default": "N/D"},
            },
        }
    )
    result = ScraplingEngine(settings=settings, adaptive=False).scrape_html(books_v1, URL, spec)
    assert [r["isbn"] for r in result.data] == ["N/D"] * 3


def test_selector_xpath(settings, books_v1):
    spec = parse_spec(
        {
            "name": "x",
            "item_selector": "article.product_pod",
            "fields": {"precio": {"selector": ".//p[@class='price_color']", "type": "xpath"}},
        }
    )
    result = ScraplingEngine(settings=settings).scrape_html(books_v1, URL, spec)
    assert [r["precio"] for r in result.data] == PRECIOS


def test_html_vacio_reporta_error(settings, books_spec):
    result = ScraplingEngine(settings=settings).scrape_html(
        "<html><body><p>nada</p></body></html>", URL, books_spec
    )
    assert not result.ok
    assert "No se extrajo ningún registro" in result.errors[0]


def test_modo_invalido(settings):
    with pytest.raises(ValueError, match="Modo desconocido"):
        ScraplingEngine(settings=settings, mode="turbo")

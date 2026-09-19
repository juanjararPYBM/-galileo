"""Test de adaptabilidad: mismo contenido, HTML reestructurado.

``books_v1.html`` y ``books_v2_redesign.html`` tienen los mismos datos pero
estructura y clases distintas (``article.product_pod`` -> ``div.catalogue-entry``,
``h3`` -> ``h2``, ``p.price_color`` -> ``span.amount``, un nivel más de anidamiento).
Ningún selector del spec encuentra nada en la v2 por la vía normal: si la segunda
corrida devuelve los mismos datos, es gracias al modo adaptativo.
"""

from __future__ import annotations

from scraper.engines.scrapling_engine import ScraplingEngine

URL = "https://books.toscrape.com/"
TITULOS = ["A Light in the Attic", "Tipping the Velvet", "Soumission"]
PRECIOS = ["£51.77", "£53.74", "£50.10"]


def test_sin_adaptativo_la_v2_no_extrae_nada(settings, books_spec, books_v2):
    """Prueba de control: los selectores viejos están realmente rotos en la v2."""
    result = ScraplingEngine(settings=settings, adaptive=False).scrape_html(
        books_v2, URL, books_spec
    )
    assert result.data == []
    assert not result.ok


def test_segunda_corrida_se_recupera_del_rediseno(settings, books_spec, books_v1, books_v2):
    engine = ScraplingEngine(settings=settings, adaptive=True)

    # 1ª corrida sobre el HTML original: extrae y guarda la huella de los elementos.
    primera = engine.scrape_html(books_v1, URL, books_spec)
    assert [r["titulo"] for r in primera.data] == TITULOS
    assert primera.meta["relocated"] is False

    # 2ª corrida sobre el HTML rediseñado: los selectores ya no valen,
    # pero el modo adaptativo reubica los elementos por su huella.
    segunda = engine.scrape_html(books_v2, URL, books_spec)

    assert segunda.ok, segunda.errors
    assert segunda.meta["relocated"] is True
    # Los datos recuperados son exactamente los mismos, campo a campo.
    assert segunda.data == primera.data


def test_la_huella_se_guarda_en_el_directorio_de_estado(settings, books_spec, books_v1):
    engine = ScraplingEngine(settings=settings, adaptive=True)
    assert not settings.adaptive_db_path.exists()

    engine.scrape_html(books_v1, URL, books_spec)

    assert settings.adaptive_db_path.exists(), "la huella debe persistir en state_dir"
    assert settings.adaptive_db_path.stat().st_size > 0


def test_sin_primera_corrida_no_hay_huella_que_reubicar(settings, books_spec, books_v2):
    """Sin datos guardados, el modo adaptativo no puede inventar nada."""
    result = ScraplingEngine(settings=settings, adaptive=True).scrape_html(
        books_v2, URL, books_spec
    )
    assert result.data == []

"""Corridas por lotes: sesiones reutilizadas y descarga concurrente.

Todo contra la réplica local (127.0.0.1), así que no necesita internet.
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from examples.local_books_site import serve_in_background  # noqa: E402

from scraper.engines.scrapling_engine import ScraplingEngine  # noqa: E402
from scraper.politeness import (  # noqa: E402
    AsyncPolitenessGate,
    AsyncRateLimiter,
    RobotsNotAllowed,
    RobotsPolicy,
)
from scraper.spec import load_spec  # noqa: E402

from conftest import FIXTURES  # noqa: E402


@pytest.fixture(scope="module")
def dos_sitios():
    """Dos servidores en puertos distintos = dos dominios a efectos de cortesía."""
    servidor_a, url_a = serve_in_background()
    servidor_b, url_b = serve_in_background()
    yield url_a, url_b
    servidor_a.shutdown()
    servidor_b.shutdown()


@pytest.fixture
def spec():
    parsed = load_spec(FIXTURES / "books_spec.yaml")
    parsed.pagination = None
    return parsed


def urls_de(sitio: str) -> list[str]:
    return [sitio, sitio + "page-2.html", sitio + "page-3.html"]


# --------------------------------------------------------------- agrupación
def test_agrupa_por_dominio():
    grupos = ScraplingEngine._group_by_domain(
        ["https://a.com/1", "https://b.com/1", "https://a.com/2"]
    )
    assert list(grupos) == ["https://a.com", "https://b.com"]
    assert grupos["https://a.com"] == ["https://a.com/1", "https://a.com/2"]


# ----------------------------------------------------------------- sesiones
def test_la_sesion_se_abre_y_se_cierra(settings, dos_sitios):
    engine = ScraplingEngine(settings=settings)
    assert engine._session is None
    with engine.session(dos_sitios[0]):
        assert engine._session is not None, "dentro del bloque debe haber sesión"
    assert engine._session is None, "al salir debe quedar limpia"


def test_scrape_many_da_lo_mismo_que_scrape(settings, spec, dos_sitios):
    sitio = dos_sitios[0]
    urls = urls_de(sitio)
    engine = ScraplingEngine(settings=settings)

    uno_a_uno = [engine.scrape(u, spec) for u in urls]
    por_lotes = engine.scrape_many(urls, spec)

    assert [r.data for r in por_lotes] == [r.data for r in uno_a_uno]
    assert all(r.ok for r in por_lotes)


def test_scrape_many_respeta_el_orden_de_entrada(settings, spec, dos_sitios):
    sitio_a, sitio_b = dos_sitios
    # Mezclamos los dominios para que el agrupado tenga que reordenar por dentro.
    urls = [sitio_a, sitio_b, sitio_a + "page-2.html", sitio_b + "page-2.html"]
    resultados = ScraplingEngine(settings=settings).scrape_many(urls, spec)
    assert [r.url for r in resultados] == urls


# -------------------------------------------------------------------- async
def test_ascrape_many_da_lo_mismo_que_scrape(settings, spec, dos_sitios):
    urls = urls_de(dos_sitios[0])
    engine = ScraplingEngine(settings=settings)

    sincrono = [engine.scrape(u, spec) for u in urls]
    asincrono = asyncio.run(engine.ascrape_many(urls, spec))

    assert [r.data for r in asincrono] == [r.data for r in sincrono]
    assert all(r.ok for r in asincrono)
    assert all(len(r.data) == 20 for r in asincrono)


def test_ascrape_many_respeta_el_orden_de_entrada(settings, spec, dos_sitios):
    sitio_a, sitio_b = dos_sitios
    urls = [sitio_b, sitio_a, sitio_b + "page-2.html", sitio_a + "page-3.html"]
    resultados = asyncio.run(ScraplingEngine(settings=settings).ascrape_many(urls, spec))
    assert [r.url for r in resultados] == urls


def test_dos_dominios_van_en_paralelo(settings, spec, dos_sitios):
    """Con 0.4 s por dominio, dos dominios en paralelo tardan lo que uno solo."""
    sitio_a, sitio_b = dos_sitios
    settings.rate_limit_seconds = 0.4
    urls = urls_de(sitio_a) + urls_de(sitio_b)

    inicio = time.perf_counter()
    resultados = asyncio.run(ScraplingEngine(settings=settings).ascrape_many(urls, spec))
    transcurrido = time.perf_counter() - inicio

    assert all(r.ok for r in resultados)
    assert len(resultados) == 6
    # Secuencial serían ~2.0s (5 esperas); en paralelo son ~0.8s (2 esperas por dominio).
    assert transcurrido < 1.6, f"no se solaparon los dominios: {transcurrido:.2f}s"


def test_el_rate_limit_por_dominio_sigue_aplicandose(settings, spec, dos_sitios):
    """La concurrencia NO debe saltarse el intervalo dentro de un mismo dominio."""
    sitio = dos_sitios[0]
    settings.rate_limit_seconds = 0.4

    inicio = time.perf_counter()
    resultados = asyncio.run(
        ScraplingEngine(settings=settings).ascrape_many(urls_de(sitio), spec, concurrency=10)
    )
    transcurrido = time.perf_counter() - inicio

    assert all(r.ok for r in resultados)
    # 3 páginas del mismo sitio = 2 esperas de 0.4s, aunque pidamos 10 en paralelo.
    assert transcurrido >= 0.8, f"se saltó el rate limit: {transcurrido:.2f}s"


def test_async_respeta_robots(settings, spec, dos_sitios):
    gate = AsyncPolitenessGate(
        robots=RobotsPolicy("bot", fetcher=lambda _: "User-agent: *\nDisallow: /"),
        limiter=AsyncRateLimiter(0.0),
    )
    resultados = asyncio.run(
        ScraplingEngine(settings=settings).ascrape_many(urls_de(dos_sitios[0]), spec, gate=gate)
    )
    assert not any(r.ok for r in resultados)
    assert all("robots.txt" in r.errors[0] for r in resultados)


def test_una_url_mala_no_tumba_el_lote(settings, spec, dos_sitios):
    """Cada URL lleva su error dentro de su propio ScrapeResult."""
    sitio = dos_sitios[0]
    urls = [sitio, sitio + "no-existe.html", sitio + "page-2.html"]

    resultados = asyncio.run(ScraplingEngine(settings=settings).ascrape_many(urls, spec))

    assert len(resultados) == 3
    assert resultados[0].ok and resultados[2].ok
    assert not resultados[1].ok


def test_la_puerta_asincrona_aplica_crawl_delay():
    gate = AsyncPolitenessGate(
        robots=RobotsPolicy("bot", fetcher=lambda _: "User-agent: *\nCrawl-delay: 7"),
        limiter=AsyncRateLimiter(1.0),
    )

    async def correr():
        await gate.before_request("https://sitio.com/a")
        return gate.limiter.interval_for("https://sitio.com")

    assert asyncio.run(correr()) == 7.0


# ------------------------------------------------------------------ la CLI
def _escribir_urls(tmp_path, urls):
    fichero = tmp_path / "urls.txt"
    fichero.write_text(
        "# comentario que debe ignorarse\n\n" + "\n".join(urls) + "\n", encoding="utf-8"
    )
    return fichero


@pytest.fixture
def cli_env(monkeypatch, tmp_path):
    monkeypatch.setenv("SCRAPER_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("SCRAPER_RATE_LIMIT_SECONDS", "0")


def test_cli_batch_en_paralelo(tmp_path, dos_sitios, cli_env):
    import json

    from typer.testing import CliRunner

    from scraper.cli import app

    fichero = _escribir_urls(tmp_path, urls_de(dos_sitios[0]) + urls_de(dos_sitios[1]))
    salida = tmp_path / "lote.json"

    resultado = CliRunner().invoke(
        app,
        ["batch", "--urls-file", str(fichero), "--spec", str(FIXTURES / "books_spec.yaml"),
         "--max-pages", "1", "--out", str(salida)],
    )

    assert resultado.exit_code == 0, resultado.output
    assert "6 URLs" in resultado.output and "2 dominio" in resultado.output
    payload = json.loads(salida.read_text(encoding="utf-8"))
    assert len(payload) == 6
    assert sum(len(p["data"]) for p in payload) == 120


def test_cli_batch_secuencial(tmp_path, dos_sitios, cli_env):
    from typer.testing import CliRunner

    from scraper.cli import app

    fichero = _escribir_urls(tmp_path, urls_de(dos_sitios[0]))
    resultado = CliRunner().invoke(
        app,
        ["batch", "--urls-file", str(fichero), "--spec", str(FIXTURES / "books_spec.yaml"),
         "--max-pages", "1", "--sequential"],
    )
    assert resultado.exit_code == 0, resultado.output
    assert "secuencial" in resultado.output


def test_cli_batch_ignora_comentarios_y_lineas_vacias(tmp_path, dos_sitios, cli_env):
    from typer.testing import CliRunner

    from scraper.cli import app

    fichero = _escribir_urls(tmp_path, [dos_sitios[0]])
    resultado = CliRunner().invoke(
        app,
        ["batch", "--urls-file", str(fichero), "--spec", str(FIXTURES / "books_spec.yaml"),
         "--max-pages", "1"],
    )
    assert resultado.exit_code == 0, resultado.output
    assert "1 URLs" in resultado.output


def test_cli_batch_con_fichero_vacio(tmp_path, cli_env):
    from typer.testing import CliRunner

    from scraper.cli import app

    fichero = tmp_path / "vacio.txt"
    fichero.write_text("# solo comentarios\n", encoding="utf-8")
    resultado = CliRunner().invoke(
        app,
        ["batch", "--urls-file", str(fichero), "--spec", str(FIXTURES / "books_spec.yaml")],
    )
    assert resultado.exit_code == 2
    assert "no tiene ninguna URL" in resultado.output

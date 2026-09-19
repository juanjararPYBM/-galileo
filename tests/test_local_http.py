"""Extremo a extremo sobre HTTP real, contra una réplica local del sitio.

No necesita internet (todo va a 127.0.0.1), pero sí ejercita de verdad la
descarga, el robots.txt del servidor, el rate limit y la paginación.
"""

from __future__ import annotations

import sys
from glob import glob
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from examples.local_books_site import serve_in_background  # noqa: E402

from scraper.engines.scrapling_engine import ScraplingEngine  # noqa: E402
from scraper.politeness import RobotsPolicy  # noqa: E402
from scraper.spec import load_spec  # noqa: E402

from conftest import FIXTURES  # noqa: E402


@pytest.fixture(scope="module")
def sitio():
    servidor, url = serve_in_background()
    yield url
    servidor.shutdown()


@pytest.fixture
def spec():
    return load_spec(FIXTURES / "books_spec.yaml")


def test_descarga_y_extrae_una_pagina(settings, spec, sitio):
    spec.pagination = None
    result = ScraplingEngine(settings=settings).scrape(sitio, spec)

    assert result.ok, result.errors
    assert len(result.data) == 20
    assert result.data[0]["titulo"] == "A Light in the Attic"
    assert result.data[0]["precio"] == "£51.77"
    assert result.data[0]["disponibilidad"] == "In stock"


def test_pagina_las_tres_paginas(settings, spec, sitio):
    result = ScraplingEngine(settings=settings).scrape(sitio, spec)

    assert result.ok, result.errors
    assert result.meta["pages"] == 3
    assert len(result.data) == 60
    assert all(fila["titulo"] and fila["precio"] for fila in result.data)


def test_lee_el_robots_txt_del_servidor(settings, sitio):
    policy = RobotsPolicy(settings.user_agent, timeout=10.0)
    assert policy._parser_for(sitio) is not None, "debe haber leído /robots.txt"
    assert policy.can_fetch(sitio) is True


def test_el_rate_limit_se_aplica_de_verdad(settings, spec, sitio):
    """Con 3 páginas y 0.3 s de intervalo, la corrida no puede durar menos de 0.6 s."""
    settings.rate_limit_seconds = 0.3
    result = ScraplingEngine(settings=settings).scrape(sitio, spec)

    assert result.meta["pages"] == 3
    assert result.duration_s >= 0.6, f"fue demasiado rápido: {result.duration_s:.2f}s"


def _chromium_instalado() -> str | None:
    """Chromium ya presente en la máquina, si Playwright no trae el suyo."""
    for patron in (
        "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
        "/opt/pw-browsers/chromium-*/chrome-linux64/chrome",
    ):
        encontrados = sorted(glob(patron))
        if encontrados:
            return encontrados[-1]
    return None


@pytest.mark.parametrize("mode", ["dynamic", "stealth"])
def test_modos_con_navegador(settings, spec, sitio, mode):
    """Modos 'dynamic' y 'stealth'. Se saltan si no hay navegador utilizable."""
    chromium = _chromium_instalado()
    if chromium:
        settings.browser_executable_path = chromium
    spec.pagination = None

    result = ScraplingEngine(settings=settings, mode=mode).scrape(sitio, spec)

    if not result.ok and "Executable doesn't exist" in result.errors[0]:
        pytest.skip("no hay un navegador compatible instalado (ejecuta: scrapling install)")
    assert result.ok, result.errors
    assert len(result.data) == 20
    assert result.data[0]["titulo"] == "A Light in the Attic"

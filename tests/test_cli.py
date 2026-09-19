"""CLI: run, ask y compare, con la red sustituida por fixtures."""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from scraper import cli as cli_module
from scraper.cli import app
from scraper.engines.scrapling_engine import ScraplingEngine
from scraper.models import ScrapeResult

from conftest import FIXTURES, read_fixture

runner = CliRunner()
URL = "https://books.toscrape.com/"
SPEC = str(FIXTURES / "books_spec.yaml")


@pytest.fixture(autouse=True)
def sin_red(monkeypatch, tmp_path):
    """El motor lee de fixture; el LLM devuelve una respuesta fija."""

    def fake_fetch(self, url):
        return self.parse_html(read_fixture("books_v1.html"), url)

    monkeypatch.setattr(ScraplingEngine, "_fetch", fake_fetch)
    monkeypatch.setenv("SCRAPER_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("SCRAPER_RATE_LIMIT_SECONDS", "0")

    class FakeLLM:
        def __init__(self, *args, **kwargs):
            pass

        def scrape(self, url, spec):
            return ScrapeResult(
                url=url,
                engine="llm",
                data={"libros": [{"titulo": "A Light in the Attic", "precio": "£51.77"}]},
                duration_s=0.4,
            )

    monkeypatch.setattr(cli_module, "LLMEngine", FakeLLM)


def test_ayuda():
    resultado = runner.invoke(app, ["--help"])
    assert resultado.exit_code == 0
    for comando in ("run", "ask", "compare"):
        assert comando in resultado.output


def test_run_imprime_tabla_y_guarda_json(tmp_path):
    salida = tmp_path / "data.json"
    resultado = runner.invoke(
        app, ["run", "--url", URL, "--spec", SPEC, "--max-pages", "1", "--out", str(salida)]
    )

    assert resultado.exit_code == 0, resultado.output
    assert "A Light in the Attic" in resultado.output
    payload = json.loads(salida.read_text(encoding="utf-8"))
    assert payload["engine"] == "scrapling"
    assert len(payload["data"]) == 3


def test_run_guarda_csv(tmp_path):
    salida = tmp_path / "data.csv"
    resultado = runner.invoke(
        app, ["run", "--url", URL, "--spec", SPEC, "--max-pages", "1", "--out", str(salida)]
    )
    assert resultado.exit_code == 0
    assert "titulo" in salida.read_text(encoding="utf-8")


def test_run_con_modo_invalido_falla():
    resultado = runner.invoke(app, ["run", "--url", URL, "--spec", SPEC, "--mode", "turbo"])
    assert resultado.exit_code != 0


def test_ask_imprime_json(tmp_path):
    salida = tmp_path / "ask.json"
    resultado = runner.invoke(
        app,
        ["ask", "--url", URL, "--prompt", "extrae título y precio", "--out", str(salida)],
    )
    assert resultado.exit_code == 0, resultado.output
    assert json.loads(salida.read_text(encoding="utf-8"))["engine"] == "llm"


def test_compare_muestra_la_tabla_comparativa(tmp_path):
    salida = tmp_path / "cmp.json"
    resultado = runner.invoke(
        app,
        [
            "compare", "--url", URL, "--spec", SPEC, "--max-pages", "1",
            "--prompt", "extrae título y precio", "--out", str(salida),
        ],
    )

    assert resultado.exit_code == 0, resultado.output
    assert "Comparación de motores" in resultado.output
    assert "tiempo" in resultado.output and "filas" in resultado.output
    payload = json.loads(salida.read_text(encoding="utf-8"))
    assert [p["engine"] for p in payload] == ["scrapling", "llm"]


def test_compare_no_acepta_max_pages_sin_spec():
    resultado = runner.invoke(app, ["compare", "--url", URL, "--prompt", "x"])
    assert resultado.exit_code != 0


def test_ignore_robots_avisa_en_el_log(tmp_path):
    resultado = runner.invoke(
        app,
        ["run", "--url", URL, "--spec", SPEC, "--max-pages", "1", "--ignore-robots"],
    )
    assert resultado.exit_code == 0
    assert "DESACTIVADO" in resultado.output

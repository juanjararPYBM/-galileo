"""Motor LLM: validación de esquema y reintento, sin necesidad de modelo."""

from __future__ import annotations

import json

import pytest
from pydantic import BaseModel

from scraper.engines.llm_engine import (
    AskSpec,
    LLMEngine,
    SchemaValidationError,
    load_schema,
    schema_from_json_schema,
)
from scraper.politeness import PolitenessGate, RateLimiter, RobotsPolicy

URL = "https://books.toscrape.com/"

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "libros": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string"},
                    "precio": {"type": "string"},
                    "stock": {"type": "boolean"},
                },
                "required": ["titulo", "precio"],
            },
        }
    },
    "required": ["libros"],
}

VALIDO = {"libros": [{"titulo": "A Light in the Attic", "precio": "£51.77", "stock": True}]}


@pytest.fixture
def open_gate():
    return PolitenessGate(
        robots=RobotsPolicy("bot", fetcher=lambda _: None), limiter=RateLimiter(0.0)
    )


class FakeGraph:
    """Sustituye a SmartScraperGraph: devuelve respuestas preparadas."""

    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.llamadas = 0

    def __call__(self, prompt, source, config, schema):
        self.prompt, self.source, self.config, self.schema = prompt, source, config, schema
        return self

    def run(self):
        self.llamadas += 1
        respuesta = self.respuestas.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        return respuesta


HTML = "<html><body><h3>A Light in the Attic</h3></body></html>"


def make_engine(llm_settings, open_gate, respuestas, html=HTML):
    """Motor con el grafo y la descarga sustituidos: ni modelo ni red."""
    graph = FakeGraph(respuestas)
    engine = LLMEngine(
        settings=llm_settings,
        gate=open_gate,
        graph_factory=graph,
        html_fetcher=lambda url: html,
    )
    return engine, graph


# ------------------------------------------------------- conversión de esquema
def test_json_schema_a_modelo_pydantic():
    modelo = schema_from_json_schema(JSON_SCHEMA, "Libros")
    assert issubclass(modelo, BaseModel)
    assert modelo.model_validate(VALIDO).model_dump()["libros"][0]["titulo"] == "A Light in the Attic"


def test_campos_opcionales_admiten_ausencia():
    modelo = schema_from_json_schema(JSON_SCHEMA, "Libros")
    datos = modelo.model_validate({"libros": [{"titulo": "X", "precio": "1"}]}).model_dump()
    assert datos["libros"][0]["stock"] is None


def test_schema_desde_fichero(tmp_path):
    path = tmp_path / "schema.json"
    path.write_text(json.dumps(JSON_SCHEMA), encoding="utf-8")
    assert load_schema(str(path)).model_validate(VALIDO)


def test_schema_sin_propiedades_falla():
    with pytest.raises(ValueError):
        schema_from_json_schema({"type": "object", "properties": {}})


# --------------------------------------------------------------- validación
def test_salida_valida(llm_settings, open_gate):
    engine, graph = make_engine(llm_settings, open_gate, [VALIDO])
    modelo = schema_from_json_schema(JSON_SCHEMA, "Libros")

    result = engine.scrape(URL, AskSpec(prompt="extrae los libros", schema=modelo))

    assert result.ok, result.errors
    assert result.engine == "llm"
    assert result.data["libros"][0]["precio"] == "£51.77"
    assert result.meta["attempts"] == 1
    assert graph.llamadas == 1


def test_salida_en_texto_json_se_parsea(llm_settings, open_gate):
    engine, _ = make_engine(llm_settings, open_gate, [json.dumps(VALIDO)])
    modelo = schema_from_json_schema(JSON_SCHEMA, "Libros")
    assert engine.scrape(URL, AskSpec(prompt="x", schema=modelo)).ok


def test_salida_invalida_reintenta_una_vez_y_acierta(llm_settings, open_gate):
    engine, graph = make_engine(llm_settings, open_gate, [{"otra_cosa": 1}, VALIDO])
    modelo = schema_from_json_schema(JSON_SCHEMA, "Libros")

    result = engine.scrape(URL, AskSpec(prompt="x", schema=modelo))

    assert result.ok, result.errors
    assert graph.llamadas == 2
    assert result.meta["attempts"] == 2


def test_si_falla_dos_veces_se_marca_error(llm_settings, open_gate):
    engine, graph = make_engine(llm_settings, open_gate, [{"mal": 1}, {"peor": 2}])
    modelo = schema_from_json_schema(JSON_SCHEMA, "Libros")

    result = engine.scrape(URL, AskSpec(prompt="x", schema=modelo))

    assert not result.ok
    assert graph.llamadas == 2
    assert "SchemaValidationError" in result.errors[0]


def test_sin_esquema_se_devuelve_lo_que_venga(llm_settings, open_gate):
    engine, _ = make_engine(llm_settings, open_gate, [{"cualquier": "cosa"}])
    result = engine.scrape(URL, AskSpec(prompt="x"))
    assert result.ok and result.data == {"cualquier": "cosa"}


def test_un_fallo_del_modelo_no_se_reintenta(llm_settings, open_gate):
    """Un error de conexión no es un problema de formato: no tiene sentido repetir."""
    engine, graph = make_engine(llm_settings, open_gate, [ConnectionError("modelo caído"), VALIDO])
    result = engine.scrape(URL, AskSpec(prompt="x"))

    assert not result.ok
    assert graph.llamadas == 1
    assert "ConnectionError" in result.errors[0]


def test_json_malformado_se_reporta(llm_settings, open_gate):
    engine, _ = make_engine(llm_settings, open_gate, ["esto no es json", "tampoco"])
    modelo = schema_from_json_schema(JSON_SCHEMA, "Libros")
    result = engine.scrape(URL, AskSpec(prompt="x", schema=modelo))
    assert not result.ok


def test_respeta_robots(llm_settings):
    gate = PolitenessGate(
        robots=RobotsPolicy("bot", fetcher=lambda _: "User-agent: *\nDisallow: /"),
        limiter=RateLimiter(0.0),
    )
    engine = LLMEngine(
        settings=llm_settings,
        gate=gate,
        graph_factory=FakeGraph([VALIDO]),
        html_fetcher=lambda url: HTML,
    )
    llm_settings.llm_prefetch = False  # la puerta se cruza antes de pedir nada
    result = engine.scrape(URL, AskSpec(prompt="x"))
    assert not result.ok and "robots.txt" in result.errors[0]


# ------------------------------------------------------------------- config
def test_config_por_defecto_apunta_a_ollama(llm_settings):
    config = llm_settings.llm_graph_config()
    assert config["llm"]["model"] == f"ollama/{llm_settings.llm_model}"
    assert config["llm"]["base_url"] == llm_settings.llm_base_url
    assert "api_key" not in config["llm"]


def test_proveedor_alternativo_usa_la_clave_del_entorno(monkeypatch):
    from scraper.config import Settings

    monkeypatch.setenv("SCRAPER_LLM_PROVIDER", "openai")
    monkeypatch.setenv("SCRAPER_LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("SCRAPER_LLM_API_KEY", "clave-de-prueba")

    config = Settings(_env_file=None).llm_graph_config()
    assert config["llm"]["model"] == "openai/gpt-4o-mini"
    assert config["llm"]["api_key"] == "clave-de-prueba"


def test_la_config_se_pasa_tal_cual_al_grafo(llm_settings, open_gate):
    engine, graph = make_engine(llm_settings, open_gate, [VALIDO])
    engine.scrape(URL, AskSpec(prompt="dame los libros"))
    assert graph.prompt == "dame los libros"
    assert graph.config == llm_settings.llm_graph_config()


def test_por_defecto_se_le_pasa_el_html_ya_descargado(llm_settings, open_gate):
    """Con prefetch, ScrapeGraphAI recibe el HTML y no abre su propio navegador."""
    engine, graph = make_engine(llm_settings, open_gate, [VALIDO])
    engine.scrape(URL, AskSpec(prompt="x"))
    assert graph.source == HTML
    assert not graph.source.startswith("http")


def test_sin_prefetch_se_le_pasa_la_url(llm_settings, open_gate):
    llm_settings.llm_prefetch = False
    engine, graph = make_engine(llm_settings, open_gate, [VALIDO])
    engine.scrape(URL, AskSpec(prompt="x"))
    assert graph.source == URL


def test_la_pagina_se_descarga_una_sola_vez_aunque_haya_reintento(llm_settings, open_gate):
    descargas = {"n": 0}

    def contando(url):
        descargas["n"] += 1
        return HTML

    graph = FakeGraph([{"mal": 1}, VALIDO])
    engine = LLMEngine(
        settings=llm_settings, gate=open_gate, graph_factory=graph, html_fetcher=contando
    )
    modelo = schema_from_json_schema(JSON_SCHEMA, "Libros")
    result = engine.scrape(URL, AskSpec(prompt="x", schema=modelo))

    assert result.ok, result.errors
    assert graph.llamadas == 2, "debe reintentar con el modelo"
    assert descargas["n"] == 1, "no debe volver a pedir la página"


# ------------------------------------------------------------ marcado @llm
@pytest.mark.llm
def test_extraccion_real_con_ollama(llm_settings):
    """Se salta solo si Ollama no responde (ver conftest)."""
    modelo = schema_from_json_schema(JSON_SCHEMA, "Libros")
    result = LLMEngine(settings=llm_settings).scrape(
        URL, AskSpec(prompt="Extrae los libros con su título y su precio", schema=modelo)
    )
    assert result.ok, result.errors
    assert result.data["libros"]

"""Salida a JSON, CSV y SQLite."""

from __future__ import annotations

import csv
import json
import sqlite3

import pytest

from scraper.models import ScrapeResult
from scraper.storage import write_csv, write_json, write_many, write_result, write_sqlite

FILAS = [
    {"titulo": "A Light in the Attic", "precio": "£51.77", "tags": ["a", "b"]},
    {"titulo": "Soumission", "precio": "£50.10", "tags": []},
]


@pytest.fixture
def result():
    return ScrapeResult(
        url="https://books.toscrape.com/",
        engine="scrapling",
        data=list(FILAS),
        duration_s=1.5,
        meta={"pages": 1},
    )


def test_json_incluye_datos_y_metadatos(result, tmp_path):
    path = write_json(result, tmp_path / "out.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["engine"] == "scrapling"
    assert payload["ok"] is True
    assert payload["meta"]["pages"] == 1
    assert payload["data"][0]["titulo"] == "A Light in the Attic"
    assert "timestamp" in payload and "duration_s" in payload


def test_csv_tiene_cabecera_y_filas(result, tmp_path):
    path = write_csv(result, tmp_path / "out.csv")
    with path.open(encoding="utf-8") as handle:
        filas = list(csv.DictReader(handle))

    assert [f["titulo"] for f in filas] == ["A Light in the Attic", "Soumission"]
    assert filas[0]["tags"] == "a | b"  # las listas se aplanan


def test_csv_sin_datos_escribe_solo_cabecera(tmp_path):
    vacio = ScrapeResult(url="u", engine="e", data=[])
    contenido = write_csv(vacio, tmp_path / "v.csv").read_text(encoding="utf-8")
    assert contenido.strip() == "value"


def test_sqlite_una_fila_por_registro(result, tmp_path):
    path = write_sqlite(result, tmp_path / "out.db")
    connection = sqlite3.connect(path)
    try:
        filas = connection.execute("SELECT url, engine, payload FROM results").fetchall()
    finally:
        connection.close()

    assert len(filas) == 2
    assert json.loads(filas[0][2])["titulo"] == "A Light in the Attic"


def test_sqlite_rechaza_nombres_de_tabla_raros(result, tmp_path):
    with pytest.raises(ValueError):
        write_sqlite(result, tmp_path / "x.db", table="results; DROP TABLE x")


def test_el_formato_se_deduce_de_la_extension(result, tmp_path):
    assert write_result(result, tmp_path / "a.csv").suffix == ".csv"
    assert json.loads(write_result(result, tmp_path / "a.json").read_text())["engine"] == "scrapling"


def test_formato_forzado(result, tmp_path):
    path = write_result(result, tmp_path / "sin_extension", fmt="csv")
    assert "titulo" in path.read_text(encoding="utf-8")


def test_formato_no_soportado(result, tmp_path):
    with pytest.raises(ValueError, match="Formato no soportado"):
        write_result(result, tmp_path / "a.xml")


def test_crea_los_directorios_que_falten(result, tmp_path):
    path = write_json(result, tmp_path / "a" / "b" / "c.json")
    assert path.exists()


def test_write_many(result, tmp_path):
    otro = ScrapeResult(url="u", engine="llm", data={"libros": []})
    payload = json.loads(write_many([result, otro], tmp_path / "ambos.json").read_text())
    assert [p["engine"] for p in payload] == ["scrapling", "llm"]


# ------------------------------------------------- normalización de registros
def test_records_normaliza_la_salida_del_llm():
    envuelto = ScrapeResult(url="u", engine="llm", data={"libros": [{"t": 1}, {"t": 2}]})
    assert envuelto.records == [{"t": 1}, {"t": 2}]


def test_records_con_dict_simple():
    assert ScrapeResult(url="u", engine="llm", data={"a": 1}).records == [{"a": 1}]


def test_records_sin_datos():
    assert ScrapeResult(url="u", engine="x").records == []


def test_ok_depende_de_los_errores():
    result = ScrapeResult(url="u", engine="x", data=[])
    assert result.ok
    result.add_error("algo")
    assert not result.ok

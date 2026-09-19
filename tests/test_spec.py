"""Parseo del spec de selectores."""

from __future__ import annotations

import json

import pytest

from scraper.spec import load_spec, parse_spec, split_pseudo


@pytest.mark.parametrize(
    ("selector", "expected"),
    [
        ("h3 a::attr(title)", ("h3 a", "attr", "title")),
        (".price_color::text", (".price_color", "text", None)),
        ("article.product_pod", ("article.product_pod", "text", None)),
        ("a::attr( data-id )", ("a", "attr", "data-id")),
        ("  .x::text  ", (".x", "text", None)),
    ],
)
def test_split_pseudo(selector, expected):
    assert split_pseudo(selector) == expected


def test_spec_desde_yaml(books_spec):
    assert books_spec.name == "books"
    assert books_spec.item_selector == "article.product_pod"
    assert books_spec.field_names == ["titulo", "precio", "disponibilidad", "enlace"]
    assert books_spec.pagination.max_pages == 3
    assert books_spec.pagination.next_selector == "li.next a"

    titulo = books_spec.fields[0]
    assert (titulo.selector, titulo.extractor, titulo.attr) == ("h3 a", "attr", "title")


def test_spec_campo_como_string_simple():
    spec = parse_spec({"fields": {"titulo": "h1::text"}})
    assert spec.fields[0].selector == "h1"
    assert spec.fields[0].many is False


def test_spec_campo_lista_y_xpath():
    spec = parse_spec(
        {"fields": {"tags": {"selector": "//li/@data-tag", "type": "xpath", "many": True}}}
    )
    campo = spec.fields[0]
    assert campo.kind == "xpath" and campo.many is True


def test_spec_identificador_por_defecto_es_el_nombre():
    spec = parse_spec({"fields": {"precio": ".p::text"}})
    assert spec.fields[0].storage_identifier == "precio"


def test_spec_json(tmp_path):
    path = tmp_path / "s.json"
    path.write_text(json.dumps({"name": "x", "fields": {"t": "h1::text"}}), encoding="utf-8")
    assert load_spec(path).name == "x"


@pytest.mark.parametrize(
    "raw",
    [
        {},
        {"fields": {}},
        {"fields": {"t": {}}},
        {"fields": {"t": "h1"}, "pagination": {"max_pages": 2}},
    ],
)
def test_spec_invalido(raw):
    with pytest.raises(ValueError):
        parse_spec(raw)

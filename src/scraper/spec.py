"""Spec de selectores: campo -> selector CSS/XPath, en YAML o JSON."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

# Sufijos tipo Scrapy que admitimos en un selector: ::text y ::attr(nombre).
_PSEUDO_RE = re.compile(r"::(text|attr\(\s*([\w:.-]+)\s*\))\s*$")

Extractor = Literal["text", "attr", "html"]


@dataclass(slots=True)
class FieldSpec:
    """Un campo a extraer."""

    name: str
    selector: str
    kind: Literal["css", "xpath"] = "css"
    many: bool = False
    extractor: Extractor = "text"
    attr: str | None = None
    identifier: str | None = None
    default: Any = None

    @property
    def storage_identifier(self) -> str:
        """Clave con la que se guarda la huella del elemento en el modo adaptativo."""
        return self.identifier or self.name


@dataclass(slots=True)
class PaginationSpec:
    next_selector: str
    kind: Literal["css", "xpath"] = "css"
    max_pages: int = 1


@dataclass(slots=True)
class ScrapeSpec:
    """Spec completo: campos, item raíz opcional y paginación opcional."""

    fields: list[FieldSpec]
    name: str = "spec"
    item_selector: str | None = None
    item_kind: Literal["css", "xpath"] = "css"
    pagination: PaginationSpec | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def field_names(self) -> list[str]:
        return [f.name for f in self.fields]


def split_pseudo(selector: str) -> tuple[str, Extractor, str | None]:
    """Separa ``div.x::attr(href)`` en ``("div.x", "attr", "href")``.

    Lo hacemos nosotros (en vez de dejárselo a Scrapling) porque cuando el modo
    adaptativo reubica un elemento devuelve el elemento, no el nodo de texto:
    extrayendo a mano, la ruta normal y la adaptativa dan exactamente lo mismo.
    """
    selector = selector.strip()
    match = _PSEUDO_RE.search(selector)
    if not match:
        return selector, "text", None
    base = selector[: match.start()].strip()
    if match.group(1) == "text":
        return base, "text", None
    return base, "attr", match.group(2)


def _coerce_field(name: str, raw: Any) -> FieldSpec:
    if isinstance(raw, str):
        raw = {"selector": raw}
    if not isinstance(raw, dict):
        raise ValueError(f"Campo '{name}': se esperaba un string o un mapa, no {type(raw).__name__}")

    selector = raw.get("selector") or raw.get("css") or raw.get("xpath")
    if not selector:
        raise ValueError(f"Campo '{name}': falta 'selector'")

    kind: Literal["css", "xpath"] = "css"
    if "xpath" in raw and "selector" not in raw and "css" not in raw:
        kind = "xpath"
    declared = raw.get("type") or raw.get("kind")
    if declared in ("css", "xpath"):
        kind = declared

    base, extractor, attr = split_pseudo(str(selector))
    if raw.get("attr"):
        extractor, attr = "attr", str(raw["attr"])
    if raw.get("extractor") in ("text", "attr", "html"):
        extractor = raw["extractor"]
    if raw.get("html") is True:
        extractor = "html"

    return FieldSpec(
        name=name,
        selector=base,
        kind=kind,
        many=bool(raw.get("many", raw.get("list", False))),
        extractor=extractor,
        attr=attr,
        identifier=raw.get("identifier"),
        default=raw.get("default"),
    )


def parse_spec(raw: dict[str, Any]) -> ScrapeSpec:
    """Construye un :class:`ScrapeSpec` a partir de un dict (YAML/JSON ya cargado)."""
    if not isinstance(raw, dict):
        raise ValueError("El spec debe ser un mapa en la raíz")

    raw_fields = raw.get("fields")
    if not raw_fields or not isinstance(raw_fields, dict):
        raise ValueError("El spec necesita una sección 'fields' con al menos un campo")

    fields = [_coerce_field(name, value) for name, value in raw_fields.items()]

    item_selector = raw.get("item_selector") or raw.get("item")
    item_kind: Literal["css", "xpath"] = "css"
    if item_selector:
        item_selector, _, _ = split_pseudo(str(item_selector))
        if str(raw.get("item_type", "")) == "xpath":
            item_kind = "xpath"

    pagination = None
    raw_pag = raw.get("pagination")
    if raw_pag:
        if not isinstance(raw_pag, dict):
            raise ValueError("'pagination' debe ser un mapa")
        next_sel = raw_pag.get("next_selector") or raw_pag.get("next")
        if not next_sel:
            raise ValueError("'pagination' necesita 'next_selector'")
        base, _, _ = split_pseudo(str(next_sel))
        pagination = PaginationSpec(
            next_selector=base,
            kind="xpath" if raw_pag.get("type") == "xpath" else "css",
            max_pages=int(raw_pag.get("max_pages", 1)),
        )

    return ScrapeSpec(
        fields=fields,
        name=str(raw.get("name", "spec")),
        item_selector=item_selector,
        item_kind=item_kind,
        pagination=pagination,
        meta=dict(raw.get("meta") or {}),
    )


def load_spec(path: str | Path) -> ScrapeSpec:
    """Carga un spec desde un fichero YAML o JSON."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        raw = json.loads(text)
    else:
        raw = yaml.safe_load(text)
    return parse_spec(raw)

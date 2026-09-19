"""Motor de extracción en lenguaje natural, sobre ScrapeGraphAI.

Entrada: URL + prompt + (opcional) esquema de salida (modelo pydantic o JSON Schema).
Proveedor por defecto: Ollama local. El proveedor alternativo se configura por
``.env``; ninguna clave se escribe en el código.

API verificada contra scrapegraphai 2.2.4:
``SmartScraperGraph(prompt: str, source: str, config: dict, schema: type[BaseModel] | None).run()``
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Type

from pydantic import BaseModel, ValidationError, create_model

from ..config import Settings, get_settings
from ..models import ScrapeResult
from ..politeness import PolitenessGate, RateLimiter, RobotsPolicy
from .base import ScrapeEngine

log = logging.getLogger("scraper.llm")

_JSON_TYPES: dict[str, Any] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "object": dict,
    "array": list,
}


@dataclass(slots=True)
class AskSpec:
    """Petición para el motor LLM."""

    prompt: str
    schema: Type[BaseModel] | None = None
    name: str = "ask"


class SchemaValidationError(ValueError):
    """La salida del modelo no cumple el esquema pedido."""


def schema_from_json_schema(json_schema: dict[str, Any], name: str = "Salida") -> Type[BaseModel]:
    """Convierte un JSON Schema sencillo en un modelo pydantic.

    Soporta objetos con propiedades escalares, objetos anidados y arrays
    (incluidos arrays de objetos), que es lo que se usa en la práctica para
    describir la salida de una extracción.
    """
    if json_schema.get("type") == "array":
        item_schema = json_schema.get("items") or {"type": "object"}
        item_model = schema_from_json_schema(item_schema, name=f"{name}Item")
        return create_model(name, items=(list[item_model], ...))  # type: ignore[valid-type]

    properties = json_schema.get("properties") or {}
    required = set(json_schema.get("required") or [])
    fields: dict[str, Any] = {}

    for prop, definition in properties.items():
        if not isinstance(definition, dict):
            definition = {"type": "string"}
        prop_type = definition.get("type", "string")

        if prop_type == "object":
            annotation: Any = schema_from_json_schema(definition, name=f"{name}_{prop}".title())
        elif prop_type == "array":
            item_def = definition.get("items") or {"type": "string"}
            if isinstance(item_def, dict) and item_def.get("type") == "object":
                inner = schema_from_json_schema(item_def, name=f"{name}_{prop}Item".title())
                annotation = list[inner]  # type: ignore[valid-type]
            else:
                inner_type = _JSON_TYPES.get(
                    (item_def or {}).get("type", "string") if isinstance(item_def, dict) else "string",
                    str,
                )
                annotation = list[inner_type]  # type: ignore[valid-type]
        else:
            annotation = _JSON_TYPES.get(prop_type, str)

        if prop in required:
            fields[prop] = (annotation, ...)
        else:
            fields[prop] = (annotation | None, None)

    if not fields:
        raise ValueError("El JSON Schema no declara ninguna propiedad")
    return create_model(name, **fields)  # type: ignore[call-overload]


def load_schema(path: str) -> Type[BaseModel]:
    """Carga un JSON Schema desde fichero y lo convierte en modelo pydantic."""
    with open(path, encoding="utf-8") as handle:
        return schema_from_json_schema(json.load(handle))


def ollama_available(base_url: str, timeout: float = 3.0) -> bool:
    """¿Responde el servidor Ollama? Lo usan los tests para saltarse solos."""
    try:
        from urllib.request import urlopen

        with urlopen(f"{base_url.rstrip('/')}/api/tags", timeout=timeout) as response:  # noqa: S310
            return response.status == 200
    except Exception:  # noqa: BLE001
        return False


class LLMEngine(ScrapeEngine):
    """Extrae datos describiendo en lenguaje natural lo que se quiere."""

    name = "llm"

    def __init__(
        self,
        settings: Settings | None = None,
        gate: PolitenessGate | None = None,
        graph_factory: Any | None = None,
        html_fetcher: Any | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.gate = gate or PolitenessGate(
            robots=RobotsPolicy(
                user_agent=self.settings.user_agent,
                enabled=self.settings.respect_robots,
                timeout=self.settings.request_timeout,
            ),
            limiter=RateLimiter(self.settings.rate_limit_seconds),
        )
        # Inyectables para poder probar la validación y el reintento sin modelo ni red.
        self._graph_factory = graph_factory or self._default_graph_factory
        self._html_fetcher = html_fetcher

    @staticmethod
    def _default_graph_factory(prompt: str, source: str, config: dict, schema: Any):
        from scrapegraphai.graphs import SmartScraperGraph

        return SmartScraperGraph(prompt=prompt, source=source, config=config, schema=schema)

    def _fetch_html(self, url: str) -> str:
        """Descarga el HTML con el motor de selectores (robots.txt, rate limit, reintentos)."""
        if self._html_fetcher is not None:
            return self._html_fetcher(url)
        from .scrapling_engine import ScraplingEngine

        engine = ScraplingEngine(settings=self.settings, gate=self.gate, adaptive=False)
        return engine._fetch(url).html_content

    def _source_for(self, url: str) -> str:
        """Qué se le pasa a ScrapeGraphAI: el HTML ya descargado, o la URL.

        ScrapeGraphAI trata como contenido local cualquier ``source`` que no empiece
        por ``http``, así que pasarle el HTML evita que abra su propio navegador.
        """
        if not self.settings.llm_prefetch:
            self.gate.before_request(url)
            return url
        return self._fetch_html(url)

    def _run_graph(self, source: str, spec: AskSpec) -> Any:
        graph = self._graph_factory(
            spec.prompt, source, self.settings.llm_graph_config(), spec.schema
        )
        return graph.run()

    @staticmethod
    def _validate(raw: Any, schema: Type[BaseModel] | None) -> Any:
        if schema is None:
            return raw
        payload = raw
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise SchemaValidationError(f"La salida no es JSON válido: {exc}") from exc
        if isinstance(payload, BaseModel):
            payload = payload.model_dump()
        try:
            return schema.model_validate(payload).model_dump()
        except ValidationError as exc:
            raise SchemaValidationError(str(exc)) from exc

    def scrape(self, url: str, spec: AskSpec) -> ScrapeResult:
        """Ejecuta el grafo. Si la salida no cumple el esquema, reintenta una vez."""
        with self._timed(
            url,
            provider=self.settings.llm_provider,
            model=self.settings.llm_model,
            prompt=spec.prompt,
            schema=spec.schema.__name__ if spec.schema else None,
            prefetch=self.settings.llm_prefetch,
        ) as result:
            attempts = 0
            last_error: Exception | None = None
            source: str | None = None

            for attempts in (1, 2):
                try:
                    # La página se descarga una sola vez: el reintento por esquema
                    # vuelve a preguntarle al modelo, no al sitio.
                    if source is None:
                        source = self._source_for(url)
                    raw = self._run_graph(source, spec)
                    result.data = self._validate(raw, spec.schema)
                    result.meta["attempts"] = attempts
                    return result
                except SchemaValidationError as exc:
                    last_error = exc
                    log.warning(
                        "La salida no cumple el esquema (intento %s/2): %s", attempts, exc
                    )
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
                    log.warning("Fallo del motor LLM (intento %s/2): %s", attempts, exc)
                    break

            result.meta["attempts"] = attempts
            result.add_error(
                f"{type(last_error).__name__}: {last_error}"
                if last_error
                else "El motor LLM no devolvió datos"
            )
        return result

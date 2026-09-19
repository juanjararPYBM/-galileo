"""Motor de scraping por selectores, sobre Scrapling.

Modos disponibles:

``fetcher``
    Petición HTTP simple (sin navegador). Rápido, para HTML estático.
``dynamic``
    Navegador real (Playwright) que ejecuta JavaScript.
``stealth``
    Navegador con contramedidas anti-bot (``StealthyFetcher``).

Selectores adaptativos
----------------------
Con ``adaptive`` activo, la primera corrida guarda la "huella" de cada elemento
encontrado (etiqueta, atributos, texto, posición en el árbol) en una base SQLite.
Si en una corrida posterior el selector ya no encuentra nada porque cambió el
HTML, Scrapling reubica el elemento comparando huellas y se vuelve a guardar la
nueva posición. La huella se guarda en ``<state_dir>/elements_storage.db``
(por defecto ``.scraper_state/elements_storage.db`` en la raíz del proyecto).
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Literal
from urllib.parse import urljoin

from scrapling import DynamicFetcher, Fetcher, Selector, StealthyFetcher

from ..config import Settings, get_settings
from ..models import ScrapeResult
from ..politeness import PolitenessGate, RateLimiter, RobotsPolicy, RetryPolicy, with_retries
from ..spec import FieldSpec, ScrapeSpec
from .base import ScrapeEngine

log = logging.getLogger("scraper.scrapling")

Mode = Literal["fetcher", "dynamic", "stealth"]
MODES: tuple[Mode, ...] = ("fetcher", "dynamic", "stealth")

# Atributos cuyo valor cambia legítimamente de un item a otro: si se comparan,
# elementos hermanos del mismo tipo (dos titulos, dos precios) parecen distintos.
# Se ignoran para que la comparación se apoye en los atributos estructurales
# (sobre todo ``class``), que son los que sí distinguen una columna de otra.
VARYING_ATTRIBUTES: tuple[str, ...] = (
    "href",
    "src",
    "title",
    "alt",
    "id",
    "name",
    "value",
    "data-id",
)


def _document_order(root: Any) -> dict[int, int]:
    """Índice ``id(elemento) -> posición`` para ordenar resultados reubicados."""
    return {id(element): index for index, element in enumerate(root.iter())}


class ScraplingEngine(ScrapeEngine):
    """Extrae campos a partir de un spec de selectores."""

    name = "scrapling"

    def __init__(
        self,
        settings: Settings | None = None,
        mode: Mode = "fetcher",
        gate: PolitenessGate | None = None,
        adaptive: bool | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        if mode not in MODES:
            raise ValueError(f"Modo desconocido '{mode}'. Usa uno de: {', '.join(MODES)}")
        self.mode: Mode = mode
        self.adaptive = self.settings.adaptive if adaptive is None else adaptive
        self.gate = gate or PolitenessGate(
            robots=RobotsPolicy(
                user_agent=self.settings.user_agent,
                enabled=self.settings.respect_robots,
                timeout=self.settings.request_timeout,
            ),
            limiter=RateLimiter(self.settings.rate_limit_seconds),
        )
        self._retry = RetryPolicy(
            max_retries=self.settings.max_retries,
            backoff_factor=self.settings.backoff_factor,
        )

    # ------------------------------------------------------------------ red
    def _selector_config(self, url: str) -> dict[str, Any]:
        if not self.adaptive:
            return {"adaptive": False}
        self.settings.ensure_state_dir()
        return {
            "adaptive": True,
            "storage_args": {
                "storage_file": str(self.settings.adaptive_db_path),
                "url": url,
            },
        }

    def _fetch(self, url: str) -> Selector:
        """Descarga la página aplicando robots.txt, rate limit y reintentos."""
        self.gate.before_request(url)
        selector_config = self._selector_config(url)
        headers = {"User-Agent": self.settings.user_agent}

        def _do() -> Selector:
            if self.mode == "fetcher":
                return Fetcher.get(
                    url,
                    headers=headers,
                    timeout=self.settings.request_timeout,
                    stealthy_headers=False,
                    follow_redirects=True,
                    selector_config=selector_config,
                )
            browser: dict[str, Any] = {}
            if self.settings.browser_executable_path:
                browser["executable_path"] = self.settings.browser_executable_path
            if self.mode == "dynamic":
                return DynamicFetcher.fetch(
                    url,
                    headless=True,
                    network_idle=True,
                    useragent=self.settings.user_agent,
                    timeout=self.settings.request_timeout * 1000,
                    selector_config=selector_config,
                    **browser,
                )
            return StealthyFetcher.fetch(
                url,
                headless=True,
                network_idle=True,
                timeout=self.settings.request_timeout * 1000,
                selector_config=selector_config,
                **browser,
            )

        response = with_retries(_do, policy=self._retry)
        status = getattr(response, "status", None)
        if status is not None and status >= 400:
            raise RuntimeError(f"HTTP {status} al pedir {url}")
        return response  # type: ignore[return-value]

    def parse_html(self, html: str, url: str) -> Selector:
        """Construye un ``Selector`` desde HTML en memoria (usado por los tests)."""
        return Selector(content=html, url=url, **self._selector_config(url))

    # -------------------------------------------------------------- extraer
    def _raw_query(
        self,
        node: Any,
        selector: str,
        kind: str,
        identifier: str,
        adaptive: bool,
        auto_save: bool,
    ) -> list[Any]:
        method: Callable[..., Any] = node.xpath if kind == "xpath" else node.css
        try:
            found = method(
                selector,
                identifier=identifier,
                adaptive=adaptive,
                auto_save=auto_save,
                percentage=self.settings.adaptive_percentage,
            )
        except TypeError:  # pragma: no cover - fetchers antiguos sin modo adaptativo
            found = method(selector)
        return list(found or [])

    def _find(
        self, node: Any, selector: str, kind: str, identifier: str
    ) -> tuple[list[Any], bool]:
        """Busca elementos y dice si hubo que reubicarlos.

        Ruta normal: el selector encuentra algo y se (re)guarda su huella.
        Ruta de curación: el selector ya no encuentra nada, así que se reubica por
        la huella guardada y se expande a los hermanos equivalentes.
        """
        plain = self._raw_query(node, selector, kind, identifier, False, self.adaptive)
        if plain:
            return plain, False
        if not self.adaptive:
            return [], False
        relocated = self._raw_query(node, selector, kind, identifier, True, True)
        if not relocated:
            return [], False
        return self._expand_similar(relocated, node), True

    def _expand_similar(self, elements: list[Any], root: Any) -> list[Any]:
        """Completa una reubicación con los elementos hermanos equivalentes.

        Scrapling guarda la huella de un solo elemento (el primero), así que al
        reubicar recupera uno; el resto de la columna se obtiene con
        ``find_similar`` y se devuelve todo en orden de documento.
        """
        if not elements:
            return elements
        try:
            similar = list(
                elements[0].find_similar(
                    similarity_threshold=self.settings.adaptive_similarity,
                    ignore_attributes=VARYING_ATTRIBUTES,
                )
                or []
            )
        except Exception as exc:  # noqa: BLE001
            log.debug("find_similar falló: %s", exc)
            return elements
        if not similar:
            return elements

        combined: list[Any] = []
        seen: set[int] = set()
        for element in [*elements, *similar]:
            key = id(getattr(element, "_root", element))
            if key not in seen:
                seen.add(key)
                combined.append(element)
        try:
            order = _document_order(root._root)
            combined.sort(key=lambda el: order.get(id(el._root), 1 << 30))
        except Exception as exc:  # noqa: BLE001
            log.debug("No se pudo ordenar por documento: %s", exc)
        return combined

    @staticmethod
    def _value_of(element: Any, field: FieldSpec) -> Any:
        if field.extractor == "attr" and field.attr:
            value = element.attrib.get(field.attr)
            return value.strip() if isinstance(value, str) else value
        if field.extractor == "html":
            return element.html_content
        text = element.get_all_text(strip=True)
        return text.strip() if isinstance(text, str) else text

    def _values(self, elements: list[Any], field: FieldSpec) -> Any:
        if not elements:
            return [] if field.many else field.default
        if field.many:
            return [self._value_of(element, field) for element in elements]
        return self._value_of(elements[0], field)

    def _extract_field_local(self, node: Any, field: FieldSpec) -> Any:
        """Extrae un campo dentro de un item, sin curación (el item ya acotó el ámbito)."""
        elements = self._raw_query(node, field.selector, field.kind, field.storage_identifier, False, False)
        return self._values(elements, field)

    def _extract_items(self, root: Any, spec: ScrapeSpec) -> tuple[list[dict[str, Any]], bool]:
        """Devuelve (registros, se_usó_reubicación)."""
        if not spec.item_selector:
            healed = False
            record: dict[str, Any] = {}
            for field in spec.fields:
                elements, relocated = self._find(
                    root, field.selector, field.kind, field.storage_identifier
                )
                healed = healed or relocated
                record[field.name] = self._values(elements, field)
            return [record], healed

        items, healed = self._find(root, spec.item_selector, spec.item_kind, f"{spec.name}:item")
        if not items:
            # El contenedor del item es puramente estructural: su huella es débil y
            # un rediseño agresivo la deja por debajo del umbral. Los campos, en
            # cambio, llevan texto y atributos, así que reubican mucho mejor:
            # reconstruimos los registros columna a columna a partir de ellos.
            if self.adaptive:
                rebuilt = self._rebuild_from_fields(root, spec)
                if rebuilt:
                    return rebuilt, True
            return [], healed

        records = [
            {field.name: self._extract_field_local(item, field) for field in spec.fields}
            for item in items
        ]

        # Para cada campo consultamos también a nivel de documento: así se refresca
        # la huella en la corrida normal y, si el campo quedó vacío en todos los
        # items, se reparten por posición los elementos reubicados.
        for field in spec.fields:
            elements, relocated = self._find(
                root, field.selector, field.kind, field.storage_identifier
            )
            if any(_has_value(record[field.name]) for record in records):
                continue
            if not elements:
                continue
            healed = healed or relocated
            for record, element in zip(records, elements):
                value = self._value_of(element, field)
                record[field.name] = [value] if field.many else value
        return records, healed

    def _rebuild_from_fields(self, root: Any, spec: ScrapeSpec) -> list[dict[str, Any]]:
        """Reubica cada campo a nivel de documento y arma los registros por posición.

        Se usa cuando el selector del item ya no encuentra nada: en la práctica es
        la vía que salva una corrida después de un rediseño fuerte del HTML.
        """
        columns: dict[str, list[Any]] = {}
        for field in spec.fields:
            elements, _ = self._find(root, field.selector, field.kind, field.storage_identifier)
            columns[field.name] = [self._value_of(element, field) for element in elements]

        height = max((len(values) for values in columns.values()), default=0)
        if height == 0:
            return []

        records: list[dict[str, Any]] = []
        for index in range(height):
            record: dict[str, Any] = {}
            for field in spec.fields:
                values = columns[field.name]
                value = values[index] if index < len(values) else field.default
                record[field.name] = ([value] if value is not None else []) if field.many else value
            records.append(record)
        return records

    def _next_url(self, root: Any, spec: ScrapeSpec, current_url: str) -> str | None:
        if not spec.pagination:
            return None
        found, _ = self._find(
            root, spec.pagination.next_selector, spec.pagination.kind, f"{spec.name}:next"
        )
        if not found:
            return None
        href = found[0].attrib.get("href") or found[0].get_all_text(strip=True)
        if not href:
            return None
        return urljoin(current_url, str(href).strip())

    # --------------------------------------------------------------- público
    def scrape(self, url: str, spec: ScrapeSpec) -> ScrapeResult:
        max_pages = spec.pagination.max_pages if spec.pagination else 1
        with self._timed(
            url, mode=self.mode, adaptive=self.adaptive, spec=spec.name
        ) as result:
            records: list[dict[str, Any]] = []
            pages: list[str] = []
            healed_any = False
            current: str | None = url

            while current and len(pages) < max(1, max_pages):
                root = self._fetch(current)
                page_records, healed = self._extract_items(root, spec)
                healed_any = healed_any or healed
                records.extend(page_records)
                pages.append(current)
                if len(pages) >= max(1, max_pages):
                    break
                nxt = self._next_url(root, spec, current)
                if not nxt or nxt in pages:
                    break
                current = nxt

            result.data = records
            result.meta.update(
                pages=len(pages),
                page_urls=pages,
                items=len(records),
                relocated=healed_any,
            )
            if not records:
                result.add_error("No se extrajo ningún registro")
        return result

    def scrape_html(self, html: str, url: str, spec: ScrapeSpec) -> ScrapeResult:
        """Extrae desde HTML ya descargado. Sin red: es la vía que usan los tests."""
        with self._timed(url, mode="html", adaptive=self.adaptive, spec=spec.name) as result:
            root = self.parse_html(html, url)
            records, healed = self._extract_items(root, spec)
            result.data = records
            result.meta.update(pages=1, items=len(records), relocated=healed)
            if not records:
                result.add_error("No se extrajo ningún registro")
        return result


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple, str, dict)):
        return len(value) > 0
    return True

"""Interfaz común de los motores de scraping."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Iterator

from ..models import ScrapeResult


class ScrapeEngine(ABC):
    """Contrato mínimo: dada una URL y un ``spec``, devolver un :class:`ScrapeResult`.

    ``spec`` es un :class:`~scraper.spec.ScrapeSpec` para el motor de selectores y
    una petición en lenguaje natural para el motor LLM; el resultado es el mismo
    tipo en ambos casos, de modo que se pueden comparar e intercambiar.
    """

    name: str = "base"

    @abstractmethod
    def scrape(self, url: str, spec: Any) -> ScrapeResult:  # pragma: no cover
        raise NotImplementedError

    @contextmanager
    def _timed(self, url: str, **meta: Any) -> Iterator[ScrapeResult]:
        """Crea el resultado, mide la duración y captura los errores no previstos."""
        result = ScrapeResult(url=url, engine=self.name, meta=dict(meta))
        started = time.perf_counter()
        try:
            yield result
        except Exception as exc:  # noqa: BLE001 - el error viaja dentro del resultado
            result.add_error(f"{type(exc).__name__}: {exc}")
        finally:
            result.duration_s = time.perf_counter() - started

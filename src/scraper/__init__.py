"""Módulo de scraping con dos motores intercambiables.

- :class:`~scraper.engines.scrapling_engine.ScraplingEngine`: extracción por
  selectores CSS/XPath, con selectores adaptativos y modo anti-bot (Scrapling).
- :class:`~scraper.engines.llm_engine.LLMEngine`: extracción descrita en lenguaje
  natural hacia JSON, con modelo local vía Ollama (ScrapeGraphAI).

Ambos devuelven el mismo :class:`~scraper.models.ScrapeResult`.
"""

from .config import Settings, get_settings
from .engines import LLMEngine, ScrapeEngine, ScraplingEngine
from .engines.llm_engine import AskSpec, schema_from_json_schema
from .models import ScrapeResult
from .politeness import AsyncPolitenessGate, AsyncRateLimiter, PolitenessGate, RateLimiter
from .spec import FieldSpec, PaginationSpec, ScrapeSpec, load_spec, parse_spec

__version__ = "0.1.0"

__all__ = [
    "Settings",
    "get_settings",
    "ScrapeEngine",
    "ScraplingEngine",
    "LLMEngine",
    "AskSpec",
    "schema_from_json_schema",
    "ScrapeResult",
    "PolitenessGate",
    "RateLimiter",
    "AsyncPolitenessGate",
    "AsyncRateLimiter",
    "ScrapeSpec",
    "FieldSpec",
    "PaginationSpec",
    "load_spec",
    "parse_spec",
    "__version__",
]

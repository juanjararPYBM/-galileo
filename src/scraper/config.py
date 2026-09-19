"""Configuración central del módulo de scraping, leída de entorno/.env."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_STATE_DIR = PROJECT_ROOT / ".scraper_state"


class Settings(BaseSettings):
    """Ajustes del scraper.

    Todos los valores se pueden sobreescribir con variables de entorno
    con el prefijo ``SCRAPER_`` o mediante un fichero ``.env``.
    """

    model_config = SettingsConfigDict(
        env_prefix="SCRAPER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Identidad y buenas prácticas -------------------------------------
    user_agent: str = Field(
        default=(
            "scraper-galileo/0.1 (+https://github.com/juanjararPYBM/-galileo; "
            "bot educativo; contacto: ver README)"
        ),
        description="User-Agent identificable enviado en cada petición.",
    )
    respect_robots: bool = Field(
        default=True,
        description="Respetar robots.txt. Solo se desactiva de forma explícita.",
    )
    rate_limit_seconds: float = Field(
        default=2.0,
        ge=0.0,
        description="Segundos mínimos entre peticiones al mismo dominio.",
    )
    max_retries: int = Field(default=3, ge=0, description="Reintentos por petición.")
    backoff_factor: float = Field(
        default=1.0, ge=0.0, description="Base del backoff exponencial en segundos."
    )
    request_timeout: float = Field(
        default=30.0, gt=0.0, description="Timeout por petición en segundos."
    )

    # --- Motor Scrapling ---------------------------------------------------
    adaptive: bool = Field(
        default=True, description="Activa los selectores adaptativos de Scrapling."
    )
    adaptive_percentage: int = Field(
        default=40,
        ge=1,
        le=100,
        description="Similitud mínima aceptada al reubicar un elemento.",
    )
    adaptive_similarity: float = Field(
        default=0.5,
        gt=0.0,
        le=1.0,
        description=(
            "Umbral al agrupar elementos hermanos tras reubicar. El 0.2 por defecto "
            "de Scrapling mezcla columnas vecinas; 0.5 las separa."
        ),
    )
    state_dir: Path = Field(
        default=DEFAULT_STATE_DIR,
        description="Carpeta donde se guarda la huella de los elementos (SQLite).",
    )

    browser_executable_path: str | None = Field(
        default=None,
        description=(
            "Ruta al Chromium a usar en los modos 'dynamic' y 'stealth'. Solo hace "
            "falta si el navegador instalado no es el que espera Playwright."
        ),
    )

    # --- Motor LLM (ScrapeGraphAI) ----------------------------------------
    llm_provider: Literal["ollama", "openai", "custom"] = Field(
        default="ollama", description="Proveedor del modelo de lenguaje."
    )
    llm_model: str = Field(
        default="llama3.2:3b",
        description="Modelo a usar (sin el prefijo de proveedor).",
    )
    llm_base_url: str = Field(
        default="http://localhost:11434",
        description="URL base del servidor Ollama (o endpoint compatible).",
    )
    llm_api_key: str | None = Field(
        default=None,
        description="Clave del proveedor alternativo. Nunca se escribe en el código.",
    )
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    llm_model_tokens: int = Field(
        default=8192, gt=0, description="Ventana de contexto declarada al modelo."
    )
    llm_timeout: float = Field(default=180.0, gt=0.0)
    llm_prefetch: bool = Field(
        default=True,
        description=(
            "Descargar el HTML con el motor Scrapling y pasárselo a ScrapeGraphAI. "
            "Así se aplica la misma cortesía (robots.txt, rate limit, User-Agent) que "
            "en el otro motor, ambos ven el mismo HTML y no hace falta navegador. "
            "Con 'false', ScrapeGraphAI descarga por su cuenta (necesita Playwright)."
        ),
    )
    llm_verbose: bool = Field(default=False)

    @field_validator("state_dir", mode="after")
    @classmethod
    def _expand(cls, value: Path) -> Path:
        return value.expanduser()

    @property
    def adaptive_db_path(self) -> Path:
        """Fichero SQLite con las huellas de los elementos para el modo adaptativo."""
        return self.state_dir / "elements_storage.db"

    def ensure_state_dir(self) -> Path:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        return self.state_dir

    def llm_graph_config(self) -> dict:
        """Construye el ``config`` que espera ScrapeGraphAI.

        Formato verificado contra scrapegraphai 2.2.4:
        ``{"llm": {"model": "<proveedor>/<modelo>", ...}, "verbose": ..., "headless": ...}``
        """
        llm: dict = {
            "model": f"{self._provider_prefix()}/{self.llm_model}",
            "temperature": self.llm_temperature,
            "model_tokens": self.llm_model_tokens,
        }
        if self.llm_provider == "ollama":
            llm["base_url"] = self.llm_base_url
            llm["format"] = "json"
        else:
            if self.llm_api_key:
                llm["api_key"] = self.llm_api_key
            if self.llm_base_url and self.llm_provider == "custom":
                llm["base_url"] = self.llm_base_url
        return {"llm": llm, "verbose": self.llm_verbose, "headless": True}

    def _provider_prefix(self) -> str:
        # "custom" se trata como un endpoint compatible con la API de OpenAI.
        return "openai" if self.llm_provider == "custom" else self.llm_provider


_settings: Settings | None = None


def get_settings(refresh: bool = False, **overrides) -> Settings:
    """Devuelve los ajustes (cacheados). ``overrides`` crea una instancia nueva."""
    global _settings
    if overrides:
        return Settings(**overrides)
    if _settings is None or refresh:
        _settings = Settings()
    return _settings

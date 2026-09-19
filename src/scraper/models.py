"""Modelos compartidos: el resultado común a todos los motores."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

JSONValue = Any


@dataclass(slots=True)
class ScrapeResult:
    """Resultado uniforme devuelto por cualquier motor.

    Permite comparar motores y cambiar de uno a otro sin tocar el resto del código.
    """

    url: str
    engine: str
    data: JSONValue = None
    errors: list[str] = field(default_factory=list)
    duration_s: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def records(self) -> list[dict[str, Any]]:
        """Normaliza ``data`` a una lista de filas, útil para CSV y comparaciones."""
        if self.data is None:
            return []
        if isinstance(self.data, list):
            return [row if isinstance(row, dict) else {"value": row} for row in self.data]
        if isinstance(self.data, dict):
            # Un dict con una única clave que contiene una lista es el patrón
            # habitual de las salidas LLM ({"productos": [...]}).
            if len(self.data) == 1:
                only = next(iter(self.data.values()))
                if isinstance(only, list):
                    return [r if isinstance(r, dict) else {"value": r} for r in only]
            return [self.data]
        return [{"value": self.data}]

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "engine": self.engine,
            "timestamp": self.timestamp.isoformat(),
            "duration_s": round(self.duration_s, 4),
            "ok": self.ok,
            "errors": list(self.errors),
            "meta": dict(self.meta),
            "data": self.data,
        }

    def add_error(self, message: str) -> None:
        self.errors.append(message)

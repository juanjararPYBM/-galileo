"""Salida de resultados: JSON (por defecto), CSV y SQLite opcional."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from .models import ScrapeResult


def _ensure_parent(path: Path) -> Path:
    path = Path(path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_json(result: ScrapeResult, path: str | Path, indent: int = 2) -> Path:
    """Guarda el resultado completo (con metadatos) en JSON."""
    path = _ensure_parent(Path(path))
    path.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=indent, default=str),
        encoding="utf-8",
    )
    return path


def _columns(rows: list[dict[str, Any]]) -> list[str]:
    seen: list[str] = []
    for row in rows:
        for key in row:
            if key not in seen:
                seen.append(key)
    return seen


def _flatten(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        return " | ".join(str(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return value


def write_csv(result: ScrapeResult, path: str | Path) -> Path:
    """Guarda solo las filas de datos en CSV (las listas se unen con ``|``)."""
    path = _ensure_parent(Path(path))
    rows = result.records
    columns = _columns(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns or ["value"])
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _flatten(row.get(key)) for key in columns})
    return path


def write_sqlite(result: ScrapeResult, path: str | Path, table: str = "results") -> Path:
    """Guarda los resultados en SQLite (una fila por registro extraído)."""
    path = _ensure_parent(Path(path))
    if not table.isidentifier():
        raise ValueError(f"Nombre de tabla inválido: {table!r}")
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            f"""CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                engine TEXT NOT NULL,
                scraped_at TEXT NOT NULL,
                payload TEXT NOT NULL
            )"""
        )
        connection.executemany(
            f"INSERT INTO {table} (url, engine, scraped_at, payload) VALUES (?, ?, ?, ?)",
            [
                (
                    result.url,
                    result.engine,
                    result.timestamp.isoformat(),
                    json.dumps(row, ensure_ascii=False, default=str),
                )
                for row in result.records
            ],
        )
        connection.commit()
    finally:
        connection.close()
    return path


def write_result(
    result: ScrapeResult,
    path: str | Path,
    fmt: str | None = None,
    table: str = "results",
) -> Path:
    """Escribe según la extensión del fichero, o el formato indicado."""
    path = Path(path)
    fmt = (fmt or path.suffix.lstrip(".") or "json").lower()
    if fmt in ("json",):
        return write_json(result, path)
    if fmt in ("csv",):
        return write_csv(result, path)
    if fmt in ("sqlite", "db", "sqlite3"):
        return write_sqlite(result, path, table=table)
    raise ValueError(f"Formato no soportado: {fmt}")


def write_many(results: Iterable[ScrapeResult], path: str | Path) -> Path:
    """Guarda varios resultados en un único JSON (usado por ``compare``)."""
    path = _ensure_parent(Path(path))
    payload = [result.to_dict() for result in results]
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    return path

"""Interfaz de línea de comandos (typer + rich)."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import get_settings
from .engines.llm_engine import AskSpec, LLMEngine, load_schema
from .engines.scrapling_engine import MODES, ScraplingEngine
from .logging_utils import setup_logging
from .models import ScrapeResult
from .spec import load_spec
from .storage import write_many, write_result

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Scraping con dos motores: selectores (Scrapling) y lenguaje natural (ScrapeGraphAI).",
)
console = Console()

MAX_PREVIEW_ROWS = 10
MAX_CELL = 48


def _settings_from_flags(
    ignore_robots: bool,
    rate_limit: Optional[float],
    no_adaptive: bool,
    llm_model: Optional[str] = None,
    llm_provider: Optional[str] = None,
):
    overrides: dict[str, Any] = {}
    if ignore_robots:
        overrides["respect_robots"] = False
    if rate_limit is not None:
        overrides["rate_limit_seconds"] = rate_limit
    if no_adaptive:
        overrides["adaptive"] = False
    if llm_model:
        overrides["llm_model"] = llm_model
    if llm_provider:
        overrides["llm_provider"] = llm_provider
    return get_settings(**overrides) if overrides else get_settings()


def _truncate(value: Any) -> str:
    text = ", ".join(str(v) for v in value) if isinstance(value, (list, tuple)) else str(value)
    text = text.replace("\n", " ").strip()
    return text if len(text) <= MAX_CELL else text[: MAX_CELL - 1] + "…"


def _print_rows(result: ScrapeResult, title: str) -> None:
    rows = result.records
    if not rows:
        console.print(f"[yellow]{title}: sin filas[/yellow]")
        return
    columns = list(rows[0].keys())
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    table = Table(title=f"{title} — {len(rows)} filas ({result.duration_s:.2f}s)")
    for column in columns:
        table.add_column(column, overflow="fold")
    for row in rows[:MAX_PREVIEW_ROWS]:
        table.add_row(*[_truncate(row.get(column, "")) for column in columns])
    console.print(table)
    if len(rows) > MAX_PREVIEW_ROWS:
        console.print(f"[dim]… y {len(rows) - MAX_PREVIEW_ROWS} filas más[/dim]")


def _report_errors(result: ScrapeResult) -> None:
    for error in result.errors:
        console.print(f"[red]error[/red] ({result.engine}): {error}")


@app.command("run")
def run_command(
    url: str = typer.Option(..., "--url", help="URL a scrapear."),
    spec: Path = typer.Option(..., "--spec", exists=True, help="Spec de selectores (YAML/JSON)."),
    mode: str = typer.Option("fetcher", "--mode", help=f"Modo: {', '.join(MODES)}."),
    out: Optional[Path] = typer.Option(None, "--out", help="Fichero de salida (.json/.csv/.db)."),
    fmt: Optional[str] = typer.Option(None, "--format", help="Fuerza el formato de salida."),
    max_pages: Optional[int] = typer.Option(None, "--max-pages", help="Límite de páginas."),
    no_adaptive: bool = typer.Option(False, "--no-adaptive", help="Desactiva los selectores adaptativos."),
    ignore_robots: bool = typer.Option(
        False, "--ignore-robots", help="DESACTIVA robots.txt (se avisa en el log)."
    ),
    rate_limit: Optional[float] = typer.Option(None, "--rate-limit", help="Segundos entre peticiones."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Extrae datos por selectores con el motor Scrapling."""
    setup_logging(verbose=verbose)
    settings = _settings_from_flags(ignore_robots, rate_limit, no_adaptive)
    parsed = load_spec(spec)
    if max_pages is not None and parsed.pagination:
        parsed.pagination.max_pages = max_pages

    engine = ScraplingEngine(settings=settings, mode=mode)  # type: ignore[arg-type]
    result = engine.scrape(url, parsed)

    _print_rows(result, f"scrapling[{mode}]")
    if result.meta.get("relocated"):
        console.print("[cyan]nota:[/cyan] algún selector fue reubicado por el modo adaptativo.")
    _report_errors(result)
    if out:
        console.print(f"[green]guardado:[/green] {write_result(result, out, fmt)}")
    raise typer.Exit(0 if result.ok else 1)


@app.command("batch")
def batch_command(
    urls_file: Path = typer.Option(
        ..., "--urls-file", exists=True, help="Fichero con una URL por línea (# = comentario)."
    ),
    spec: Path = typer.Option(..., "--spec", exists=True, help="Spec de selectores (YAML/JSON)."),
    mode: str = typer.Option("fetcher", "--mode", help=f"Modo: {', '.join(MODES)}."),
    out: Optional[Path] = typer.Option(None, "--out", help="JSON con todos los resultados."),
    concurrency: Optional[int] = typer.Option(
        None, "--concurrency", "-c", help="Descargas simultáneas (por defecto, la de .env)."
    ),
    sequential: bool = typer.Option(
        False, "--sequential", help="Sin concurrencia, pero reutilizando la sesión."
    ),
    max_pages: Optional[int] = typer.Option(None, "--max-pages"),
    no_adaptive: bool = typer.Option(False, "--no-adaptive"),
    ignore_robots: bool = typer.Option(False, "--ignore-robots", help="DESACTIVA robots.txt."),
    rate_limit: Optional[float] = typer.Option(None, "--rate-limit"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Scrapea muchas URLs reutilizando sesión por dominio, en paralelo por defecto.

    El rate limit por dominio se sigue aplicando: la concurrencia acelera cuando hay
    varios sitios, no cuando machacas uno solo.
    """
    setup_logging(verbose=verbose)
    settings = _settings_from_flags(ignore_robots, rate_limit, no_adaptive)
    parsed = load_spec(spec)
    if max_pages is not None and parsed.pagination:
        parsed.pagination.max_pages = max_pages

    urls = _read_urls(urls_file)
    if not urls:
        console.print(f"[red]error:[/red] {urls_file} no tiene ninguna URL")
        raise typer.Exit(2)

    engine = ScraplingEngine(settings=settings, mode=mode)  # type: ignore[arg-type]
    dominios = len(ScraplingEngine._group_by_domain(urls))
    console.print(
        f"[dim]{len(urls)} URLs · {dominios} dominio(s) · "
        f"{'secuencial' if sequential else f'{concurrency or settings.concurrency} en paralelo'}[/dim]"
    )

    if sequential:
        resultados = engine.scrape_many(urls, parsed)
    else:
        resultados = asyncio.run(engine.ascrape_many(urls, parsed, concurrency=concurrency))

    console.print(_batch_table(resultados))
    fallidos = [r for r in resultados if not r.ok]
    for resultado in fallidos:
        console.print(f"[red]error[/red] {resultado.url}: {resultado.errors[0]}")
    if out:
        console.print(f"[green]guardado:[/green] {write_many(resultados, out)}")
    raise typer.Exit(0 if not fallidos else 1)


def _read_urls(path: Path) -> list[str]:
    urls: list[str] = []
    for linea in path.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            urls.append(linea)
    return urls


def _batch_table(resultados: list[ScrapeResult]) -> Table:
    filas = sum(len(r.records) for r in resultados)
    total = sum(r.duration_s for r in resultados)
    tabla = Table(title=f"Lote — {len(resultados)} URLs, {filas} filas")
    tabla.add_column("url", overflow="fold")
    tabla.add_column("filas", justify="right")
    tabla.add_column("págs", justify="right")
    tabla.add_column("seg", justify="right")
    tabla.add_column("estado")
    for resultado in resultados[:MAX_PREVIEW_ROWS]:
        tabla.add_row(
            resultado.url,
            str(len(resultado.records)),
            str(resultado.meta.get("pages", 1)),
            f"{resultado.duration_s:.2f}",
            "[green]ok[/green]" if resultado.ok else "[red]error[/red]",
        )
    if len(resultados) > MAX_PREVIEW_ROWS:
        tabla.caption = f"… y {len(resultados) - MAX_PREVIEW_ROWS} URLs más"
    tabla.add_section()
    tabla.add_row("[b]total[/b]", f"[b]{filas}[/b]", "", f"[b]{total:.2f}[/b]", "")
    return tabla


@app.command("ask")
def ask_command(
    url: str = typer.Option(..., "--url", help="URL a scrapear."),
    prompt: str = typer.Option(..., "--prompt", help="Qué extraer, en lenguaje natural."),
    schema: Optional[Path] = typer.Option(
        None, "--schema", exists=True, help="JSON Schema de la salida esperada."
    ),
    out: Optional[Path] = typer.Option(None, "--out", help="Fichero de salida (.json/.csv/.db)."),
    fmt: Optional[str] = typer.Option(None, "--format", help="Fuerza el formato de salida."),
    model: Optional[str] = typer.Option(None, "--model", help="Modelo a usar (sobrescribe .env)."),
    provider: Optional[str] = typer.Option(None, "--provider", help="ollama | openai | custom."),
    ignore_robots: bool = typer.Option(False, "--ignore-robots", help="DESACTIVA robots.txt."),
    rate_limit: Optional[float] = typer.Option(None, "--rate-limit"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Extrae datos describiendo en lenguaje natural lo que quieres."""
    setup_logging(verbose=verbose)
    settings = _settings_from_flags(ignore_robots, rate_limit, False, model, provider)
    ask = AskSpec(prompt=prompt, schema=load_schema(str(schema)) if schema else None)

    console.print(f"[dim]modelo: {settings.llm_provider}/{settings.llm_model}[/dim]")
    result = LLMEngine(settings=settings).scrape(url, ask)

    if result.ok:
        console.print_json(json.dumps(result.data, ensure_ascii=False, default=str))
    _report_errors(result)
    if out:
        console.print(f"[green]guardado:[/green] {write_result(result, out, fmt)}")
    raise typer.Exit(0 if result.ok else 1)


@app.command("compare")
def compare_command(
    url: str = typer.Option(..., "--url", help="URL a scrapear con ambos motores."),
    spec: Path = typer.Option(..., "--spec", exists=True, help="Spec para el motor Scrapling."),
    prompt: str = typer.Option(..., "--prompt", help="Prompt para el motor LLM."),
    schema: Optional[Path] = typer.Option(None, "--schema", exists=True),
    mode: str = typer.Option("fetcher", "--mode"),
    max_pages: int = typer.Option(
        1, "--max-pages", help="Páginas del motor de selectores (1 para comparar en igualdad)."
    ),
    out: Optional[Path] = typer.Option(None, "--out", help="JSON con ambos resultados."),
    ignore_robots: bool = typer.Option(False, "--ignore-robots"),
    rate_limit: Optional[float] = typer.Option(None, "--rate-limit"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Corre ambos motores sobre la misma URL y compara campos, diferencias y tiempos."""
    setup_logging(verbose=verbose)
    settings = _settings_from_flags(ignore_robots, rate_limit, False)
    parsed = load_spec(spec)
    if parsed.pagination:
        # El motor LLM solo ve la página indicada, así que por defecto limitamos
        # el de selectores a lo mismo para que la comparación sea justa.
        parsed.pagination.max_pages = max_pages

    selector_result = ScraplingEngine(settings=settings, mode=mode).scrape(url, parsed)  # type: ignore[arg-type]
    llm_result = LLMEngine(settings=settings).scrape(
        url, AskSpec(prompt=prompt, schema=load_schema(str(schema)) if schema else None)
    )

    _print_rows(selector_result, f"scrapling[{mode}]")
    _print_rows(llm_result, "llm")
    console.print(_comparison_table(selector_result, llm_result))
    for result in (selector_result, llm_result):
        _report_errors(result)
    if out:
        console.print(f"[green]guardado:[/green] {write_many([selector_result, llm_result], out)}")
    raise typer.Exit(0 if (selector_result.ok or llm_result.ok) else 1)


def _comparison_table(left: ScrapeResult, right: ScrapeResult) -> Table:
    table = Table(title="Comparación de motores")
    table.add_column("métrica")
    table.add_column(left.engine, overflow="fold")
    table.add_column(right.engine, overflow="fold")
    table.add_column("¿coincide?")

    left_rows, right_rows = left.records, right.records
    left_fields = sorted({key for row in left_rows for key in row})
    right_fields = sorted({key for row in right_rows for key in row})

    def mark(a: Any, b: Any) -> str:
        return "[green]sí[/green]" if a == b else "[yellow]no[/yellow]"

    table.add_row("tiempo (s)", f"{left.duration_s:.2f}", f"{right.duration_s:.2f}", "—")
    table.add_row("filas", str(len(left_rows)), str(len(right_rows)), mark(len(left_rows), len(right_rows)))
    table.add_row("campos", ", ".join(left_fields) or "—", ", ".join(right_fields) or "—",
                  mark(set(left_fields), set(right_fields)))
    table.add_row("errores", str(len(left.errors)), str(len(right.errors)), mark(left.errors, right.errors))

    common = [f for f in left_fields if f in right_fields]
    for field in common:
        left_first = left_rows[0].get(field) if left_rows else None
        right_first = right_rows[0].get(field) if right_rows else None
        table.add_row(
            f"1ª fila · {field}",
            _truncate(left_first if left_first is not None else "—"),
            _truncate(right_first if right_first is not None else "—"),
            mark(str(left_first).strip(), str(right_first).strip()),
        )
    only_left = [f for f in left_fields if f not in right_fields]
    only_right = [f for f in right_fields if f not in left_fields]
    if only_left or only_right:
        table.add_row("campos solo en uno", ", ".join(only_left) or "—", ", ".join(only_right) or "—", "[yellow]no[/yellow]")
    return table


def main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    main()

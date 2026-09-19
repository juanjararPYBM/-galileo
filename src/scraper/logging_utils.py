"""Log legible en consola con rich."""

from __future__ import annotations

import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console(stderr=True)


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    level = logging.WARNING if quiet else (logging.DEBUG if verbose else logging.INFO)
    root = logging.getLogger("scraper")
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(
        RichHandler(
            console=console,
            rich_tracebacks=True,
            show_path=False,
            omit_repeated_times=False,
            markup=False,
        )
    )
    root.propagate = False
    # Scrapling y ScrapeGraphAI son bastante ruidosos en modo normal.
    for noisy in ("scrapling", "scrapegraphai", "httpx", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING if not verbose else logging.INFO)

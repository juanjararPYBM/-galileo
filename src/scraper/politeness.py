"""Buenas prácticas: robots.txt, rate limit por dominio y reintentos con backoff.

Todo está activado por defecto. Las dependencias de tiempo y red se inyectan
para poder probarlo sin internet y sin esperas reales.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable
from urllib.parse import urlparse, urlunparse

from protego import Protego

log = logging.getLogger("scraper.politeness")

Clock = Callable[[], float]
Sleeper = Callable[[float], None]
RobotsFetcher = Callable[[str], str | None]


def domain_of(url: str) -> str:
    """Clave de agrupación: esquema + host + puerto."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}".lower()


def robots_url_for(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))


class RobotsNotAllowed(RuntimeError):
    """La URL está prohibida por robots.txt."""


class RateLimiter:
    """Espera lo necesario para no superar 1 petición cada ``min_interval`` por dominio."""

    def __init__(
        self,
        min_interval: float = 2.0,
        clock: Clock | None = None,
        sleeper: Sleeper | None = None,
    ) -> None:
        self.min_interval = float(min_interval)
        self._clock: Clock = clock or time.monotonic
        self._sleep: Sleeper = sleeper or time.sleep
        self._last: dict[str, float] = {}
        self._overrides: dict[str, float] = {}
        self._lock = threading.Lock()

    def set_domain_interval(self, domain: str, interval: float) -> None:
        """Intervalo específico para un dominio (p. ej. el Crawl-delay de robots.txt)."""
        with self._lock:
            self._overrides[domain] = float(interval)

    def interval_for(self, domain: str) -> float:
        return max(self.min_interval, self._overrides.get(domain, 0.0))

    def wait(self, url: str) -> float:
        """Bloquea lo que haga falta y devuelve los segundos esperados."""
        domain = domain_of(url)
        with self._lock:
            interval = self.interval_for(domain)
            now = self._clock()
            last = self._last.get(domain)
            delay = 0.0
            if last is not None:
                elapsed = now - last
                if elapsed < interval:
                    delay = interval - elapsed
            self._last[domain] = now + delay
        if delay > 0:
            log.debug("Rate limit: esperando %.2fs para %s", delay, domain)
            self._sleep(delay)
        return delay


class AsyncRateLimiter:
    """Igual que :class:`RateLimiter`, pero sin bloquear el bucle de eventos.

    El intervalo sigue siendo **por dominio**: lanzar 50 corrutinas contra el mismo
    sitio no lo acelera, y eso es lo correcto. La concurrencia rinde cuando hay
    varios dominios o cuando bajas el intervalo a conciencia.
    """

    def __init__(
        self,
        min_interval: float = 2.0,
        clock: Clock | None = None,
        sleeper: Callable[[float], Any] | None = None,
    ) -> None:
        self.min_interval = float(min_interval)
        self._clock: Clock = clock or time.monotonic
        self._sleep = sleeper
        self._last: dict[str, float] = {}
        self._overrides: dict[str, float] = {}
        self._lock: Any = None

    def set_domain_interval(self, domain: str, interval: float) -> None:
        self._overrides[domain] = float(interval)

    def interval_for(self, domain: str) -> float:
        return max(self.min_interval, self._overrides.get(domain, 0.0))

    async def wait(self, url: str) -> float:
        import asyncio

        if self._lock is None:
            self._lock = asyncio.Lock()
        domain = domain_of(url)
        async with self._lock:
            interval = self.interval_for(domain)
            now = self._clock()
            last = self._last.get(domain)
            delay = 0.0
            if last is not None and (now - last) < interval:
                delay = interval - (now - last)
            self._last[domain] = now + delay
        if delay > 0:
            log.debug("Rate limit (async): esperando %.2fs para %s", delay, domain)
            if self._sleep is not None:
                await self._sleep(delay)
            else:
                await asyncio.sleep(delay)
        return delay


class AsyncPolitenessGate:
    """Puerta asíncrona: robots.txt + rate limit antes de cada petición."""

    def __init__(
        self,
        robots: RobotsPolicy,
        limiter: AsyncRateLimiter,
        honor_crawl_delay: bool = True,
    ) -> None:
        self.robots = robots
        self.limiter = limiter
        self.honor_crawl_delay = honor_crawl_delay

    async def before_request(self, url: str) -> float:
        import asyncio

        # La lectura de robots.txt es E/S bloqueante: fuera del bucle de eventos.
        # Se cachea por dominio, así que solo la primera URL de cada sitio paga.
        permitido = await asyncio.to_thread(self.robots.can_fetch, url)
        if not permitido:
            raise RobotsNotAllowed(f"robots.txt prohíbe acceder a {url}")
        if self.honor_crawl_delay:
            delay = await asyncio.to_thread(self.robots.crawl_delay, url)
            if delay:
                self.limiter.set_domain_interval(domain_of(url), delay)
        return await self.limiter.wait(url)


async def awith_retries(
    func: Callable[[], Any],
    policy: RetryPolicy | None = None,
    sleeper: Callable[[float], Any] | None = None,
    on_retry: Callable[[int, BaseException, float], None] | None = None,
):
    """Versión asíncrona de :func:`with_retries`."""
    import asyncio

    policy = policy or RetryPolicy()
    last_error: BaseException | None = None

    for attempt in range(policy.max_retries + 1):
        try:
            return await func()
        except policy.retry_on as exc:  # type: ignore[misc]
            last_error = exc
            if attempt >= policy.max_retries:
                break
            delay = min(policy.backoff_factor * (2**attempt), policy.max_backoff)
            if on_retry:
                on_retry(attempt + 1, exc, delay)
            else:
                log.warning(
                    "Intento %s/%s falló (%s). Reintento en %.1fs",
                    attempt + 1,
                    policy.max_retries,
                    exc,
                    delay,
                )
            if delay > 0:
                await (sleeper(delay) if sleeper else asyncio.sleep(delay))

    assert last_error is not None
    raise last_error


def _default_robots_fetcher(user_agent: str, timeout: float) -> RobotsFetcher:
    def fetch(robots_url: str) -> str | None:
        try:  # import perezoso: no queremos red en los tests unitarios
            from urllib.request import Request, urlopen

            request = Request(robots_url, headers={"User-Agent": user_agent})
            with urlopen(request, timeout=timeout) as response:  # noqa: S310
                if response.status >= 400:
                    return None
                return response.read().decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001 - sin robots.txt se permite todo
            log.debug("No se pudo leer %s (%s)", robots_url, exc)
            return None

    return fetch


class RobotsPolicy:
    """Comprueba robots.txt con Protego y cachea el resultado por dominio."""

    def __init__(
        self,
        user_agent: str,
        enabled: bool = True,
        fetcher: RobotsFetcher | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.user_agent = user_agent
        self.enabled = enabled
        self._fetcher = fetcher or _default_robots_fetcher(user_agent, timeout)
        self._cache: dict[str, Protego | None] = {}
        self._lock = threading.Lock()
        if not enabled:
            log.warning(
                "robots.txt DESACTIVADO explícitamente: las peticiones ignorarán las "
                "reglas del sitio. Úsalo solo en sitios propios o con permiso."
            )

    def _parser_for(self, url: str) -> Protego | None:
        domain = domain_of(url)
        with self._lock:
            if domain in self._cache:
                return self._cache[domain]
        content = self._fetcher(robots_url_for(url))
        parser = None
        if content:
            try:
                parser = Protego.parse(content)
            except Exception as exc:  # noqa: BLE001
                log.debug("robots.txt ilegible en %s (%s)", domain, exc)
                parser = None
        with self._lock:
            self._cache[domain] = parser
        return parser

    def can_fetch(self, url: str) -> bool:
        if not self.enabled:
            return True
        parser = self._parser_for(url)
        if parser is None:  # sin robots.txt legible -> se permite
            return True
        return bool(parser.can_fetch(url, self.user_agent))

    def crawl_delay(self, url: str) -> float | None:
        if not self.enabled:
            return None
        parser = self._parser_for(url)
        if parser is None:
            return None
        delay = parser.crawl_delay(self.user_agent)
        return float(delay) if delay is not None else None

    def check(self, url: str) -> None:
        """Lanza :class:`RobotsNotAllowed` si la URL está prohibida."""
        if not self.can_fetch(url):
            raise RobotsNotAllowed(f"robots.txt prohíbe acceder a {url}")


@dataclass(slots=True)
class RetryPolicy:
    """Reintentos con backoff exponencial: ``factor * 2**intento``."""

    max_retries: int = 3
    backoff_factor: float = 1.0
    max_backoff: float = 60.0
    retry_on: tuple[type[BaseException], ...] = (Exception,)

    def delays(self) -> Iterable[float]:
        for attempt in range(self.max_retries):
            yield min(self.backoff_factor * (2**attempt), self.max_backoff)


def with_retries(
    func: Callable[[], object],
    policy: RetryPolicy | None = None,
    sleeper: Sleeper | None = None,
    on_retry: Callable[[int, BaseException, float], None] | None = None,
):
    """Ejecuta ``func`` reintentando con backoff exponencial."""
    policy = policy or RetryPolicy()
    sleep = sleeper or time.sleep
    last_error: BaseException | None = None

    for attempt in range(policy.max_retries + 1):
        try:
            return func()
        except policy.retry_on as exc:  # type: ignore[misc]
            last_error = exc
            if attempt >= policy.max_retries:
                break
            delay = min(policy.backoff_factor * (2**attempt), policy.max_backoff)
            if on_retry:
                on_retry(attempt + 1, exc, delay)
            else:
                log.warning(
                    "Intento %s/%s falló (%s). Reintento en %.1fs",
                    attempt + 1,
                    policy.max_retries,
                    exc,
                    delay,
                )
            if delay > 0:
                sleep(delay)

    assert last_error is not None
    raise last_error


class PolitenessGate:
    """Una sola puerta de entrada: robots.txt + rate limit antes de cada petición."""

    def __init__(
        self,
        robots: RobotsPolicy,
        limiter: RateLimiter,
        honor_crawl_delay: bool = True,
    ) -> None:
        self.robots = robots
        self.limiter = limiter
        self.honor_crawl_delay = honor_crawl_delay

    def before_request(self, url: str) -> float:
        """Valida robots.txt y aplica el rate limit. Devuelve la espera aplicada."""
        self.robots.check(url)
        if self.honor_crawl_delay:
            delay = self.robots.crawl_delay(url)
            if delay:
                self.limiter.set_domain_interval(domain_of(url), delay)
        return self.limiter.wait(url)

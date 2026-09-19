"""robots.txt, rate limit por dominio y reintentos con backoff (sin red, sin esperas)."""

from __future__ import annotations

import pytest

from scraper.engines.scrapling_engine import ScraplingEngine
from scraper.politeness import (
    PolitenessGate,
    RateLimiter,
    RetryPolicy,
    RobotsNotAllowed,
    RobotsPolicy,
    domain_of,
    robots_url_for,
    with_retries,
)

ROBOTS = """
User-agent: *
Disallow: /private
Crawl-delay: 5

User-agent: EvilBot
Disallow: /
"""


def robots_fetcher(_: str) -> str:
    return ROBOTS


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.slept: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds


# --------------------------------------------------------------------- robots
def test_robots_permite_y_prohibe():
    policy = RobotsPolicy("mi-bot", fetcher=robots_fetcher)
    assert policy.can_fetch("https://sitio.com/publico")
    assert not policy.can_fetch("https://sitio.com/private/datos")


def test_robots_por_user_agent():
    assert not RobotsPolicy("EvilBot", fetcher=robots_fetcher).can_fetch("https://sitio.com/x")
    assert RobotsPolicy("mi-bot", fetcher=robots_fetcher).can_fetch("https://sitio.com/x")


def test_robots_check_lanza_excepcion():
    policy = RobotsPolicy("mi-bot", fetcher=robots_fetcher)
    policy.check("https://sitio.com/ok")
    with pytest.raises(RobotsNotAllowed, match="robots.txt"):
        policy.check("https://sitio.com/private/x")


def test_robots_desactivado_permite_todo(caplog):
    policy = RobotsPolicy("mi-bot", enabled=False, fetcher=robots_fetcher)
    assert policy.can_fetch("https://sitio.com/private/x")
    assert any("DESACTIVADO" in record.message for record in caplog.records), (
        "desactivar robots.txt debe avisar en el log"
    )


def test_sin_robots_txt_se_permite():
    assert RobotsPolicy("mi-bot", fetcher=lambda _: None).can_fetch("https://sitio.com/x")


def test_robots_se_cachea_por_dominio():
    llamadas: list[str] = []

    def contando(url: str) -> str:
        llamadas.append(url)
        return ROBOTS

    policy = RobotsPolicy("mi-bot", fetcher=contando)
    for path in ("/a", "/b", "/c"):
        policy.can_fetch(f"https://sitio.com{path}")
    policy.can_fetch("https://otro.com/a")
    assert len(llamadas) == 2


def test_crawl_delay():
    assert RobotsPolicy("mi-bot", fetcher=robots_fetcher).crawl_delay("https://sitio.com/") == 5.0


def test_urls_auxiliares():
    assert domain_of("https://Sitio.com/a/b?c=1") == "https://sitio.com"
    assert robots_url_for("https://sitio.com/a/b") == "https://sitio.com/robots.txt"


# ----------------------------------------------------------------- rate limit
def test_rate_limit_espera_entre_peticiones():
    clock = FakeClock()
    limiter = RateLimiter(2.0, clock=clock, sleeper=clock.sleep)

    assert limiter.wait("https://sitio.com/a") == 0.0  # la primera no espera
    assert limiter.wait("https://sitio.com/b") == 2.0
    assert clock.slept == [2.0]


def test_rate_limit_es_por_dominio():
    clock = FakeClock()
    limiter = RateLimiter(2.0, clock=clock, sleeper=clock.sleep)

    limiter.wait("https://uno.com/a")
    assert limiter.wait("https://dos.com/a") == 0.0
    assert clock.slept == []


def test_rate_limit_no_espera_si_ya_paso_el_intervalo():
    clock = FakeClock()
    limiter = RateLimiter(2.0, clock=clock, sleeper=clock.sleep)

    limiter.wait("https://sitio.com/a")
    clock.now += 10.0
    assert limiter.wait("https://sitio.com/b") == 0.0


def test_el_crawl_delay_manda_sobre_el_intervalo_por_defecto():
    clock = FakeClock()
    gate = PolitenessGate(
        robots=RobotsPolicy("mi-bot", fetcher=robots_fetcher),
        limiter=RateLimiter(2.0, clock=clock, sleeper=clock.sleep),
    )
    gate.before_request("https://sitio.com/a")
    assert gate.before_request("https://sitio.com/b") == 5.0


def test_la_puerta_bloquea_lo_prohibido():
    gate = PolitenessGate(
        robots=RobotsPolicy("mi-bot", fetcher=robots_fetcher), limiter=RateLimiter(0.0)
    )
    with pytest.raises(RobotsNotAllowed):
        gate.before_request("https://sitio.com/private/x")


# -------------------------------------------------------------------- retries
def test_backoff_exponencial():
    clock = FakeClock()
    intentos = {"n": 0}

    def falla_dos_veces():
        intentos["n"] += 1
        if intentos["n"] < 3:
            raise ConnectionError("boom")
        return "ok"

    resultado = with_retries(
        falla_dos_veces, policy=RetryPolicy(max_retries=3, backoff_factor=1.0), sleeper=clock.sleep
    )
    assert resultado == "ok"
    assert intentos["n"] == 3
    assert clock.slept == [1.0, 2.0]  # 1*2^0, 1*2^1


def test_se_rinde_y_propaga_el_error():
    clock = FakeClock()

    def siempre_falla():
        raise ConnectionError("boom")

    with pytest.raises(ConnectionError):
        with_retries(
            siempre_falla, policy=RetryPolicy(max_retries=2, backoff_factor=1.0), sleeper=clock.sleep
        )
    assert clock.slept == [1.0, 2.0]


def test_backoff_con_techo():
    assert list(RetryPolicy(max_retries=5, backoff_factor=1.0, max_backoff=4.0).delays()) == [
        1.0,
        2.0,
        4.0,
        4.0,
        4.0,
    ]


def test_sin_reintentos_se_ejecuta_una_vez():
    intentos = {"n": 0}

    def falla():
        intentos["n"] += 1
        raise ValueError("x")

    with pytest.raises(ValueError):
        with_retries(falla, policy=RetryPolicy(max_retries=0))
    assert intentos["n"] == 1


# ------------------------------------------------- integración con el motor
def test_el_motor_no_pide_una_url_prohibida(settings, books_spec):
    engine = ScraplingEngine(
        settings=settings,
        gate=PolitenessGate(
            robots=RobotsPolicy(settings.user_agent, fetcher=robots_fetcher),
            limiter=RateLimiter(0.0),
        ),
    )
    result = engine.scrape("https://sitio.com/private/libros", books_spec)
    assert not result.ok
    assert "robots.txt" in result.errors[0]


def test_robots_activado_por_defecto(settings):
    assert settings.respect_robots is True
    assert ScraplingEngine(settings=settings).gate.robots.enabled is True

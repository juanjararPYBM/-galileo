"""Réplica local de books.toscrape.com para probar el scraper sin salir a internet.

Sirve 3 páginas con la misma estructura HTML que el sitio real (``article.product_pod``,
``h3 a[title]``, ``p.price_color``, ``p.instock.availability``, ``li.next a``) más un
``/robots.txt`` permisivo.

    python examples/local_books_site.py            # queda escuchando en 8000
    python examples/local_books_site.py --port 9000
"""

from __future__ import annotations

import argparse
import threading
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer

TITULOS = [
    "A Light in the Attic", "Tipping the Velvet", "Soumission", "Sharp Objects",
    "Sapiens: A Brief History of Humankind", "The Requiem Red", "The Dirty Little Secrets",
    "The Coming Woman", "The Boys in the Boat", "The Black Maria", "Starving Hearts",
    "Shakespeare's Sonnets", "Set Me Free", "Scott Pilgrim's Precious Little Life",
    "Rip it Up and Start Again", "Our Band Could Be Your Life", "Olio",
    "Mesaerion: The Best Science Fiction", "Libertarianism for Beginners",
    "It's Only the Himalayas",
]
PRECIOS = [
    "51.77", "53.74", "50.10", "47.82", "54.23", "22.65", "33.34", "17.93", "22.60", "52.15",
    "13.99", "20.66", "17.46", "52.29", "35.02", "57.25", "23.88", "37.59", "51.33", "45.17",
]


def _libro(indice: int, pagina: int) -> str:
    desplazado = (indice + (pagina - 1) * 7) % len(TITULOS)
    titulo = TITULOS[desplazado]
    precio = PRECIOS[(indice + (pagina - 1) * 3) % len(PRECIOS)]
    stock = "In stock" if (indice + pagina) % 5 else "Out of stock"
    slug = titulo.lower().replace(" ", "-").replace("'", "").replace(":", "")[:40]
    return f"""
      <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
        <article class="product_pod">
          <div class="image_container">
            <a href="catalogue/{slug}_{1000 - desplazado}/index.html">
              <img class="thumbnail" src="media/{slug}.jpg" alt="{titulo}"/>
            </a>
          </div>
          <p class="star-rating Three"><i class="icon-star"></i></p>
          <h3><a href="catalogue/{slug}_{1000 - desplazado}/index.html" title="{titulo}">{titulo[:25]}</a></h3>
          <div class="product_price">
            <p class="price_color">£{precio}</p>
            <p class="instock availability"><i class="icon-ok"></i> {stock}</p>
          </div>
        </article>
      </li>"""


def pagina_html(pagina: int, total: int = 3, por_pagina: int = 20) -> str:
    libros = "".join(_libro(i, pagina) for i in range(por_pagina))
    if pagina < total:
        siguiente = "page-2.html" if pagina == 1 else f"page-{pagina + 1}.html"
        pager = f'<li class="next"><a href="{siguiente}">next</a></li>'
    else:
        pager = ""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>All products | Books to Scrape (replica local)</title></head>
<body id="default" class="default">
  <div class="page_inner"><div class="content">
    <h1>All products</h1>
    <section>
      <ol class="row">{libros}
      </ol>
      <div class="pager"><ul class="pagination">
        <li class="current">Page {pagina} of {total}</li>
        {pager}
      </ul></div>
    </section>
  </div></div>
</body></html>"""


ROBOTS = "User-agent: *\nAllow: /\nCrawl-delay: 0\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        ruta = self.path.split("?")[0]
        if ruta == "/robots.txt":
            return self._responder(ROBOTS, "text/plain; charset=utf-8")
        if ruta in ("/", "/index.html"):
            return self._responder(pagina_html(1))
        for numero in (2, 3):
            if ruta in (f"/page-{numero}.html", f"/catalogue/page-{numero}.html"):
                return self._responder(pagina_html(numero))
        self.send_error(404)

    def _responder(self, cuerpo: str, tipo: str = "text/html; charset=utf-8") -> None:
        datos = cuerpo.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def log_message(self, *args) -> None:  # silencio
        pass


def serve_in_background(port: int = 0) -> tuple[HTTPServer, str]:
    """Arranca el servidor en un hilo y devuelve (servidor, url_base)."""
    servidor = HTTPServer(("127.0.0.1", port), Handler)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    return servidor, f"http://127.0.0.1:{servidor.server_port}/"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    servidor, url = serve_in_background(args.port)
    print(f"Réplica local de books.toscrape.com en {url}  (Ctrl-C para parar)")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        servidor.shutdown()


if __name__ == "__main__":
    main()

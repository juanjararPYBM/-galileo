# scraper — módulo de scraping con dos motores

Módulo reutilizable en Python con dos formas de extraer datos de una web, que
devuelven **el mismo tipo de resultado** y se pueden intercambiar y comparar:

| Motor | Librería | Cómo le dices qué quieres |
|---|---|---|
| **selectores** | [Scrapling](https://github.com/D4Vinci/Scrapling) (BSD-3) | un spec YAML/JSON: `campo → selector CSS/XPath` |
| **lenguaje natural** | [ScrapeGraphAI](https://github.com/ScrapeGraphAI/Scrapegraph-ai) (MIT) | una frase: *"extrae nombre, precio y teléfono"* |

Incluye selectores adaptativos (sobreviven a rediseños del HTML), modo anti-bot,
paginación, y robots.txt + rate limit + reintentos **activados por defecto**.

---

## 1. Requisitos e instalación

- **Python 3.12 o superior** (lo exige `scrapegraphai` 2.x).
- Recomendado [`uv`](https://docs.astral.sh/uv/); también funciona con `pip` + venv.

### Con uv (recomendado)

```bash
uv sync                  # crea el entorno e instala todo con las versiones fijadas
uv run scrapling install # descarga los navegadores (modos dynamic y stealth)
uv run playwright install
uv run scraper --help
```

### Con pip

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install "scrapling[all]" scrapegraphai
scrapling install
playwright install
scraper --help
```

`scrapling install` y `playwright install` **solo hacen falta para los modos con
navegador** (`dynamic` y `stealth`). El modo `fetcher` y el motor LLM funcionan sin ellos.

### Modelo local (motor LLM)

El motor LLM usa [Ollama](https://ollama.com) en local por defecto. Si no lo tienes:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # Linux / macOS
ollama pull llama3.2:3b                         # modelo ligero, va bien en CPU
```

Modelos ligeros que funcionan razonablemente en CPU: `llama3.2:3b` (recomendado),
`qwen2.5:3b`, `gemma2:2b`. Sin Ollama, el resto del módulo funciona igual y los
tests del motor LLM se saltan solos.

---

## 2. Configuración (`.env`)

Copia `.env.example` a `.env` y ajusta. Todas las variables llevan el prefijo
`SCRAPER_`, y también se pueden pasar como variables de entorno.

```bash
cp .env.example .env
```

Lo que más se toca:

| Variable | Por defecto | Para qué |
|---|---|---|
| `SCRAPER_USER_AGENT` | `scraper-galileo/0.1 (…)` | User-Agent identificable. **Pon un contacto real.** |
| `SCRAPER_RESPECT_ROBOTS` | `true` | Respetar robots.txt. |
| `SCRAPER_RATE_LIMIT_SECONDS` | `2.0` | Segundos entre peticiones al mismo dominio. |
| `SCRAPER_MAX_RETRIES` / `SCRAPER_BACKOFF_FACTOR` | `3` / `1.0` | Reintentos con backoff exponencial. |
| `SCRAPER_ADAPTIVE` | `true` | Selectores adaptativos. |
| `SCRAPER_STATE_DIR` | `.scraper_state` | Dónde se guarda la huella de los elementos. |
| `SCRAPER_LLM_PROVIDER` | `ollama` | `ollama`, `openai` o `custom`. |
| `SCRAPER_LLM_MODEL` | `llama3.2:3b` | Modelo del motor LLM. |
| `SCRAPER_LLM_API_KEY` | *(vacío)* | Clave del proveedor alternativo. **Solo en tu `.env` local.** |

> `.env` está en `.gitignore`. Ninguna clave aparece en el código: se leen siempre del entorno.

Para usar un proveedor de API en vez del modelo local:

```dotenv
SCRAPER_LLM_PROVIDER=openai
SCRAPER_LLM_MODEL=gpt-4o-mini
SCRAPER_LLM_API_KEY=sk-...
```

---

## 3. Uso rápido

### `scraper run` — extraer por selectores

```bash
scraper run \
  --url https://books.toscrape.com/ \
  --spec examples/books_spec.yaml \
  --max-pages 3 \
  --out data.json
```

Opciones útiles: `--mode fetcher|dynamic|stealth`, `--out data.csv` (o `.db` para
SQLite), `--no-adaptive`, `--rate-limit 5`, `--ignore-robots`, `--verbose`.

### `scraper ask` — extraer describiéndolo en lenguaje natural

```bash
scraper ask \
  --url https://books.toscrape.com/ \
  --prompt "extrae el título, el precio y la disponibilidad de cada libro" \
  --schema examples/schema_libros.json \
  --out data.json
```

### `scraper compare` — los dos motores sobre la misma página

```bash
scraper compare \
  --url https://books.toscrape.com/ \
  --spec examples/books_spec.yaml \
  --prompt "extrae el título, el precio y la disponibilidad de cada libro"
```

Imprime las filas de cada motor y una tabla con campos, diferencias y tiempos.

### Desde Python

```python
from scraper import ScraplingEngine, LLMEngine, AskSpec, load_spec

spec = load_spec("examples/books_spec.yaml")
resultado = ScraplingEngine(mode="stealth").scrape("https://books.toscrape.com/", spec)
print(resultado.ok, len(resultado.data), resultado.duration_s)

respuesta = LLMEngine().scrape(
    "https://books.toscrape.com/",
    AskSpec(prompt="extrae el título y el precio de cada libro"),
)
print(respuesta.data)
```

Ambos devuelven un `ScrapeResult` con `url`, `engine`, `timestamp`, `data`,
`errors`, `duration_s` y `meta`.

---

## 4. El spec de selectores

`campo → selector`. Admite YAML o JSON. La forma corta es un string:

```yaml
name: books
item_selector: "article.product_pod"   # opcional: una fila por cada elemento que encaje
fields:
  titulo: "h3 a::attr(title)"          # forma corta
  precio:
    selector: ".price_color::text"
  disponibilidad:
    selector: ".availability::text"
  etiquetas:
    selector: "div.tags a.tag::text"
    many: true                         # lista en vez de valor único
  descripcion:
    selector: "//div[@id='desc']/p"
    type: xpath                        # CSS por defecto
    default: "sin descripción"
pagination:
  next_selector: "li.next a::attr(href)"
  max_pages: 3
```

- `::text` toma el texto del elemento; `::attr(nombre)` toma un atributo.
  Sin sufijo, se toma el texto.
- Sin `item_selector` se devuelve **un solo registro** con todos los campos
  (útil para páginas de detalle).
- `many: true` devuelve una lista.
- Los enlaces relativos de la paginación se resuelven contra la página actual.

## 5. El prompt del motor LLM

El prompt es una frase normal. Cuanto más concreto, mejor:

```bash
--prompt "extrae, de cada libro, el título exacto, el precio con su moneda y si está en stock"
```

Puedes fijar la forma de la salida con un JSON Schema (`--schema`):

```json
{
  "type": "object",
  "properties": {
    "libros": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "titulo": { "type": "string" },
          "precio": { "type": "string" },
          "disponibilidad": { "type": "string" }
        },
        "required": ["titulo", "precio"]
      }
    }
  },
  "required": ["libros"]
}
```

Si la salida no cumple el esquema se **reintenta una vez**; si vuelve a fallar, el
resultado se marca con error (`ScrapeResult.errors`). La página se descarga **una
sola vez**: el reintento vuelve a preguntarle al modelo, no al sitio.

---

## 6. Selectores adaptativos: qué son y dónde se guarda la huella

Con `SCRAPER_ADAPTIVE=true` (por defecto):

1. **Primera corrida:** los selectores encuentran los elementos y Scrapling guarda
   su *huella* (etiqueta, atributos, texto, posición en el árbol).
2. **Corridas siguientes:** si el HTML cambió y el selector ya no encuentra nada,
   se reubica el elemento comparando huellas y se guarda la nueva posición.

**La huella se guarda en `.scraper_state/elements_storage.db`** (SQLite), en la raíz
del proyecto. Se cambia con `SCRAPER_STATE_DIR`. Está en `.gitignore`.
Borrar ese fichero equivale a empezar de cero.

Dos detalles de implementación que conviene conocer:

- Scrapling guarda la huella de **un solo elemento** (el primero). Para recuperar
  una columna entera, el módulo completa la reubicación con `find_similar()` e
  ignora los atributos que cambian de una fila a otra (`title`, `href`, `id`…),
  de modo que compare por la estructura y no por el contenido.
- El contenedor de cada fila (`item_selector`) es puramente estructural y su huella
  es débil: si un rediseño fuerte lo deja por debajo del umbral, el módulo
  reconstruye los registros **columna a columna** desde los campos, que reubican
  mucho mejor porque llevan texto y atributos.

Esto está cubierto por `tests/test_adaptive.py`, que extrae de dos HTML con la
misma información y estructura distinta y comprueba que la segunda corrida devuelve
exactamente los mismos datos.

---

## 7. Buenas prácticas (activadas por defecto)

- **robots.txt** se consulta y se respeta (con `protego`, incluido `Crawl-delay`).
  Solo se desactiva con `--ignore-robots`, y al hacerlo **queda un aviso en el log**.
- **Rate limit por dominio**: 1 petición cada 2 s por defecto. Si robots.txt declara
  un `Crawl-delay` mayor, manda ese.
- **User-Agent identificable**, configurable. Pon un contacto real.
- **Reintentos con backoff exponencial** (`factor * 2**intento`, con techo).
- Sin logins ni cookies de redes sociales.

---

## 8. Cuándo usar cada motor

**Motor de selectores (`run`)** — es el que deberías usar casi siempre:

- Es **mucho más rápido** (centésimas de segundo frente a segundos) y **gratis**:
  no gasta tokens ni necesita un modelo.
- Es **determinista y repetible**: la misma página da siempre el mismo resultado.
- Escala bien a miles de páginas y a la paginación.
- Necesita que mires el HTML una vez para escribir los selectores.

**Motor LLM (`ask`)** — para cuando los selectores no compensan:

- Exploración rápida: no sabes aún cómo es la página y quieres ver qué hay.
- Páginas **heterogéneas**: cada una tiene una estructura distinta y no hay un
  selector común (fichas de proveedores, resultados de buscadores, PDFs pasados a HTML).
- Datos que hay que **interpretar**, no solo copiar ("¿tiene envío gratis?",
  "¿en qué provincia está?").
- Pocas páginas, donde escribir el spec cuesta más que preguntarlo.

**En la práctica:** usa `ask` para explorar y entender la página, y luego escribe el
spec y pásate a `run` para la extracción de verdad. `compare` sirve justo para eso:
ver si el spec recoge lo mismo que el modelo antes de fiarte de él.

---

## 9. Tests

```bash
pytest -m "not network and not llm"   # por defecto: sin internet y sin modelo
pytest -m network                     # integración contra quotes/books.toscrape.com
pytest -m llm                         # motor LLM (se salta solo si Ollama no responde)
pytest                                # todo
```

Qué cubre la corrida por defecto (**95 tests, sin red**):

- extracción por selectores, campos de lista, XPath, valores por defecto;
- **adaptabilidad**: dos HTML con estructura distinta, misma salida;
- paginación (hasta el máximo, enlaces relativos, fin de la serie);
- robots.txt (permitir/prohibir, por User-Agent, caché, `Crawl-delay`, aviso al desactivarlo);
- rate limit por dominio y backoff exponencial, con reloj simulado (sin esperas reales);
- validación de esquema del motor LLM, reintento único y una sola descarga por consulta;
- salida a JSON, CSV y SQLite; los tres comandos de la CLI;
- **extremo a extremo sobre HTTP real** contra una réplica local del sitio
  (`examples/local_books_site.py`), incluidos los modos `dynamic` y `stealth`.

Para probar la demo sin salir a internet:

```bash
python examples/local_books_site.py &          # réplica local en :8000
scraper run --url http://127.0.0.1:8000/ --spec examples/books_spec.yaml --max-pages 3
```

---

## 10. Limitaciones conocidas

- **Python 3.12+ obligatorio**: `scrapegraphai` 2.x no soporta 3.11.
- **La reubicación adaptativa no es magia.** Reubica elementos cuyo *contenido* se
  parece al guardado. Si la página cambia de verdad (otros productos, otro idioma),
  no hay huella que valga: revisa los selectores. Y si el rediseño es tan agresivo
  que ni los campos pasan el umbral, la corrida devuelve vacío y lo dice.
- **La reconstrucción columna a columna empareja por posición.** Si tras un rediseño
  un campo falta en algunas filas, los valores pueden desalinearse. El resultado lo
  avisa con `meta["relocated"] = True`: conviene revisarlo cuando aparezca.
- **Los modos `dynamic` y `stealth` necesitan el navegador de Playwright**
  (`scrapling install`). Si tienes un Chromium que Playwright no reconoce, apúntale
  con `SCRAPER_BROWSER_EXECUTABLE_PATH`.
- **La calidad del motor LLM depende del modelo.** Los modelos de 3B fallan más al
  respetar el esquema que uno grande; hay un reintento, no más. En páginas largas el
  contexto se queda corto: sube `SCRAPER_LLM_MODEL_TOKENS` o recorta la página.
- **`compare` usa 1 página por defecto** para que la comparación sea justa: el motor
  LLM solo ve la página indicada, el de selectores podría seguir paginando.
- El motor LLM **no es determinista**: dos corridas pueden dar resultados distintos
  aunque la temperatura sea 0.
- **Sin sesión iniciada:** no hay login, ni cookies, ni rotación de proxies.

## 11. Fuera de alcance (TODO documentado, sin implementar)

- Scraping con sesión iniciada en redes sociales (tipo Agent Reach).
- Rotación de proxies de pago. *Nota: los fetchers de Scrapling ya aceptan `proxy` y
  `proxy_rotator`; bastaría con exponerlo en `Settings` y pasarlo en `_fetch`.*
- Programación periódica (cron / scheduler).
- Servidor MCP propio. *Nota: Scrapling trae uno (`scrapling mcp`), sin integrar aquí.*

## 12. Licencia

Ver `LICENSE`. Scrapling es BSD-3 y ScrapeGraphAI es MIT; ambas permiten este uso.

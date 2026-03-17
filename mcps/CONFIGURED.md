# MCPs Configurados para Galileo

## Estado: ✅ Configurados

Los siguientes MCPs están configurados en `config/mcporter.json`:

---

## MCPs Disponibles

### 1. Filesystem
**Propósito:** Leer, escribir y gestionar archivos locales

**Comandos útiles:**
```bash
# Listar archivos
mcporter call filesystem.list_directory path="/home/user/.openclaw/workspace"

# Leer archivo
mcporter call filesystem.read_text_file path="/home/user/.openclaw/workspace/GALILEO.md"

# Escribir archivo
mcporter call filesystem.write_file path="/home/user/.openclaw/workspace/test.md" content="# Hello"

# Buscar archivos
mcporter call filesystem.search_files path="/home/user/.openclaw/workspace" pattern="*.md"

# Crear directorio
mcporter call filesystem.create_directory path="/home/user/.openclaw/workspace/new-folder"
```

**Herramientas:** 14 (read_file, write_file, list_directory, search_files, etc.)

---

### 2. Memory (Knowledge Graph)
**Propósito:** Almacenamiento persistente de conocimiento

**Comandos útiles:**
```bash
# Crear entidades
mcporter call memory.create_entities entities='[{"name": "Churn Model", "entityType": "MLProject", "observations": ["Usa XGBoost", "Recall 82%"]}]'

# Crear relaciones
mcporter call memory.create_relations relations='[{"from": "Churn Model", "to": "XGBoost", "relationType": "uses_algorithm"}]'

# Buscar entidades
mcporter call memory.search_nodes query: "Churn"

# Obtener entidad
mcporter call memory.get_entity name: "Churn Model"
```

**Herramientas:** Entidades, relaciones, búsqueda en knowledge graph

---

### 3. Git
**Propósito:** Operaciones con repositorios Git

**Comandos útiles:**
```bash
# Estado del repositorio
mcporter call git.git_status

# Ver diff
mcporter call git.git_diff

# Commit reciente
mcporter call git.git_log max_count: 5

# Buscar en código
mcporter call git.grep search_term: "function" path: "."

# Branch actual
mcporter call git.get_current_branch
```

**Herramientas:** status, diff, log, grep, branch, commit, etc.

---

### 4. SQLite
**Propósito:** Consultas a bases de datos SQLite

**Comandos útiles:**
```bash
# Listar tablas
mcporter call sqlite.list_tables

# Schema de tabla
mcporter call sqlite.get_table_schema table: "users"

# Ejecutar query
mcporter call sqlite.execute_sql sql: "SELECT * FROM users LIMIT 10"

# Query con parámetros
mcporter call sqlite.execute_sql sql: "SELECT COUNT(*) as total FROM users WHERE active = ?" params: [true]
```

**Herramientas:** list_tables, get_table_schema, execute_sql

---

### 5. Fetch
**Propósito:** Obtener contenido de páginas web

**Comandos útiles:**
```bash
# Obtener página web
mcporter call fetch.fetch url: "https://github.com"

# Obtener con opciones
mcporter call fetch.fetch url: "https://api.example.com/data" max_chars: 5000
```

**Herramientas:** fetch

---

## Agregar Más MCPs

```bash
# Agregar un nuevo MCP
mcporter config add <nombre> "<comando>"

# Ejemplo: Brave Search
mcporter config add brave-search "npx -y @modelcontextprotocol/server-brave-search"

# Ejemplo: GitHub
mcporter config add github "npx -y @modelcontextprotocol/server-github"

# Verificar
mcporter config list
```

---

## Usar en el Ecosistema Galileo

Los MCPs están disponibles para que los agentes los usen a través de mcporter:

```python
# Los agentes pueden llamar MCPs así:
import subprocess

def call_mcp(server, tool, **kwargs):
    args = f"{server}.{tool} " + " ".join(f"{k}:{v}" for k,v in kwargs.items())
    result = subprocess.run(["mcporter", "call", args], capture_output=True)
    return result.stdout
```

---

## MCPs Recomendados para Agregar Después

| MCP | Comando | Propósito |
|-----|---------|-----------|
| Brave Search | `npx -y @modelcontextprotocol/server-brave-search` | Búsqueda web |
| GitHub | `npx -y @modelcontextprotocol/server-github` | Gestión repos |
| Slack | `npx -y slack-mcp-server` | Notificaciones |
| Puppeteer | `npx -y @modelcontextprotocol/server-puppeteer` | Web scraping |

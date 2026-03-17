# MCPs para Galileo

## Estado: ✅ Configurados

Los MCPs están configurados en `config/mcporter.json` y listos para usar.

Para más detalles, ver [CONFIGURED.md](./CONFIGURED.md)

## MCPs de Referencia (del repositorio oficial)

| MCP | Descripción | Relevancia para Data Science | Status |
|-----|-------------|------------------------------|--------|
| **Filesystem** | Operaciones de archivo con control de acceso | ✅ Archivos de datos, datasets | Instalar |
| **Git** | Herramientas para leer, buscar y manipular repositorios Git | ✅ Control de versiones, colaboración | Instalar |
| **Memory** | Sistema de memoria persistente basado en knowledge graph | ✅ Memoria de agentes | **Alta prioridad** |
| **Fetch** | Obtención y conversión de contenido web | ✅ Web scraping, investigación | Instalar |
| **Sequential Thinking** | Resolución de problemas mediante pensamiento secuencial | ✅ Análisis complejo | Evaluar |
| **Time** | Conversión de tiempo y timezone | ✅ Feature engineering temporal | Opcional |

---

## MCPs de Terceros - Relevancia por Fase

### Fase 1: Business Understanding

| MCP | Uso Potencial | Relevancia |
|-----|---------------|------------|
| **Web Search (Brave)** | Investigar benchmarks, competidores | Alta |
| **Slack** | Comunicar con stakeholders | Media |
| **Google Drive** | Acceder a documentos de negocio | Alta |

### Fase 2: Data Understanding

| MCP | Uso Potencial | Relevancia |
|-----|---------------|------------|
| **PostgreSQL/SQLite** | Consultar bases de datos | **Alta** |
| **Google Drive** | Acceder a spreadsheets | Alta |
| **Filesystem** | Leer archivos CSV/Excel/Parquet | **Alta** |

### Fase 3: Data Preparation

| MCP | Uso Potencial | Relevancia |
|-----|---------------|------------|
| **PostgreSQL/SQLite** | Transformaciones SQL | **Alta** |
| **Puppeteer** | Web scraping para datos | Media |
| **Filesystem** | Leer/escribir datasets | **Alta** |

### Fase 4: Modeling

| MCP | Uso Potencial | Relevancia |
|-----|---------------|------------|
| **Git** | Versionado de modelos | **Alta** |
| **GitHub** | Integración con repositorio | Alta |
| **Sentry** | Monitoreo de errores | Media |

### Fase 5: Evaluation

| MCP | Uso Potencial | Relevancia |
|-----|---------------|------------|
| **Slack/Discord** | Notificar resultados | Media |
| **Sentry** | Análisis de errores | Media |

### Fase 6: Deployment

| MCP | Uso Potencial | Relevancia |
|-----|---------------|------------|
| **AWS KB Retrieval** | Knowledge base AWS | Media |
| **Kubernetes (no disponible)** | Orquestación | Futura |
| **Docker (no disponible)** | Contenedores | Futura |

---

## MCPs Recomendados para Instalar

### 🟢 Alta Prioridad

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/data"]
    },
    "memory": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite"]
    }
  }
}
```

### 🟡 Media Prioridad

```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "github": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

---

## Evaluación Detallada

### ✅ Filesystem MCP

**Qué hace:**
- Leer, escribir, listar archivos
- Control de acceso configurable

**Para qué sirve en DS:**
- Leer datasets (CSV, Parquet, Excel)
- Guardar modelos entrenados
- Gestionar artifacts

**Instalación:**
```bash
npx -y @modelcontextprotocol/server-filesystem /home/user/data
```

---

### ✅ Git MCP

**Qué hace:**
- Leer commits, branches, diffs
- Buscar en historial
- Crear branches y commits

**Para qué sirve en DS:**
- Versionado de código y modelos
- Seguimiento de experimentos
- Colaboración en equipo

**Instalación:**
```bash
npx -y @modelcontextprotocol/server-git
```

---

### ✅ Memory MCP

**Qué hace:**
- Almacenamiento persistente
- Knowledge graph
- Retrieval de información

**Para qué sirve en DS:**
- **Memoria de agentes** ← NUESTRO CASO
- Guardar contexto entre sesiones
- Registrar lecciones aprendidas

**Instalación:**
```bash
npx -y @modelcontextprotocol/server-memory
```

---

### ✅ SQLite MCP

**Qué hace:**
- Consultas SQL
- Schema inspection
- Base de datos local

**Para qué sirve en DS:**
- Exploración de datos
- Transformaciones SQL
- Testing de queries

**Instalación:**
```bash
npx -y @modelcontextprotocol/server-sqlite
```

---

## MCPs que Podrían Interesar (Explorar Después)

| MCP | why |
|-----|-----|
| **AgentOps** | Observabilidad de agentes |
| **Sentry** | Monitoreo de errores en producción |
| **Slack/Discord** | Notificaciones |
| **Google Maps** | Datos geográficos |
| **Puppeteer** | Scraping avanzado |

---

## Siguiente Paso

¿Quieres que:

1. **Instale los MCPs de alta prioridad** en la configuración de OpenClaw?
2. **Configure el MCP de Memory** para el sistema de lecciones?
3. **Cree un MCP personalizado** para alguna necesidad específica?

¿Qué te parece?

# Investigación: MCPs Recomendados por la Comunidad

## Fuente
Repositorio: [awesome-mcp-servers](https://github.com/appcypher/awesome-mcp-servers) - Lista curada de la comunidad

---

## Resumen: MCPs por Categoría

### 🔍 Search & Web (Más Relevantes para Investigación)

| MCP | Descripción | Relevancia |
|-----|-------------|------------|
| **Brave Search** | Búsqueda web | 🟢 Alta - YA RECOMENDADO |
| **Exa Search** | Búsqueda web avanzada + crawling | 🟢 Alta |
| **Firecrawl** | Web scraping avanzado | 🟢 Alta |
| **Fetch** | Obtención de páginas web | 🟡 Media - YA TENEMOS |

### 🗄️ Databases (Para Data Science)

| MCP | Descripción | Relevancia |
|-----|-------------|------------|
| **SQLite** | Base de datos ligera | 🟢 Alta - YA TENEMOS |
| **PostgreSQL** | Base de datos relacional | 🟡 Media |
| **MongoDB** | Base de datos NoSQL | 🟡 Media |
| **Redis** | Cache y key-value | 🔴 Baja |

### 💬 Communication (Notificaciones)

| MCP | Descripción | Relevancia |
|-----|-------------|------------|
| **Slack** | Mensajería empresarial | 🟡 Media - CONSIDERAR |
| **Discord** | Mensajería comunitaria | 🟡 Media |
| **Telegram** | Mensajería | 🟡 Media |

### 🧬 Research & Data (Para Faceta 2)

| MCP | Descripción | Relevancia |
|-----|-------------|------------|
| **ArXiv** | Búsqueda de papers académicos | 🟢 Alta - INVESTIGAR |
| **PubMed** | Investigación médica | 🟡 Media |
| **Wikipedia** | Enciclopedia | 🟡 Media |

### 📂 File Systems (YA TENEMOS)

| MCP | Estado |
|-----|--------|
| Filesystem | ✅ YA CONFIGURADO |

### 🔄 Version Control (YA TENEMOS)

| MCP | Estado |
|-----|--------|
| Git | ✅ YA CONFIGURADO |

---

## Análisis Crítico: ¿Qué Nos Falta?

### MCPs que YA TENEMOS:
- ✅ filesystem
- ✅ memory
- ✅ git
- ✅ sqlite
- ✅ fetch

### MCPs RECOMENDADOS para AGREGAR:

| MCP | Prioridad | Justificación |
|-----|-----------|----------------|
| **Brave Search** | 🔴 Alta | Búsqueda web para investigación |
| **Exa Search** | 🟡 Media | Alternativa a Brave (más features) |
| **Firecrawl** | 🟡 Media | Web scraping avanzado |

### MCPs OPCIONALES (Futuro):

| MCP | Cuándo |
|-----|--------|
| Slack | Para notificaciones |
| PostgreSQL | Si datos son muy grandes |
| ArXiv | Si hacemos investigación académica |

---

## Comparación: Brave Search vs Exa Search vs Firecrawl

| Característica | Brave Search | Exa Search | Firecrawl |
|----------------|--------------|------------|-----------|
| **Tipo** | Búsqueda | Búsqueda + Crawling | Scraping |
| **Gratis** | Sí (limitado) | Sí (limitado) | Sí (limitado) |
| **API Key** | Necesaria | Necesaria | Necesaria |
| **Faceta 1 (DS)** | Investigación | Investigación | Scraping |
| **Faceta 2 (Invest)** | ✅ Ideal | ✅ Ideal | ✅ Ideal |

### Mi Recomendación:
1. **Brave Search** - Más simple, suficiente para la mayoría
2. **Firecrawl** - Solo si necesitamos scraping específico

---

## Roadmap de MCPs

### Fase 1: Essentials (YA TENEMOS)
```
✅ filesystem
✅ memory  
✅ git
✅ sqlite
✅ fetch
```

### Fase 2: Investigación (PRÓXIMO)
```
🔄 Brave Search    ← PRIORIDAD
🔄 Exa Search     ← Alternativa
```

### Fase 3: Comunicación (FUTURO)
```
📌 Slack (para notificaciones)
📌 Discord
```

### Fase 4: Datos (FUTURO)
```
📌 PostgreSQL (si datos > 1GB)
📌 ArXiv (investigación académica)
```

---

## Decisión Inmediata

### Agregar AHORA:
```bash
# Brave Search - Para investigación
mcporter config add brave-search "npx -y @modelcontextprotocol/server-brave-search"
```

### Considerar DESPUÉS:
```bash
# Firecrawl - Para scraping avanzado
mcporter config add firecrawl "npx -y @firecrawl/firecrawl-mcp-server"

# Slack - Para notificaciones
mcporter config add slack "npx -y slack-mcp-server"
```

---

## Validación de Seguridad

### Para cada MCP nuevo, verificar:

|check|Qué revisar|
|-----|-----------|
|1| Whitelist de dominios/URLs |
|2| Permisos que necesita |
|3| Datos a los que accede |
|4| Logging de operaciones |
|5| Rate limits |

### Configuración de Seguridad para Brave Search:

```json
{
  "fetch": {
    "allowed_domains": [
      "brave.com",
      "search.brave.com",
      "github.com",
      "arxiv.org",
      "wikipedia.org"
    ]
  }
}
```

---

## Conclusión

| Acción | Estado |
|--------|--------|
| Investigar MCPs | ✅ Completado |
| Recomendación Brave Search | ✅ Listo para agregar |
| Lista futuros MCPs | ✅ Documentada |

**Siguiente:** ¿Querés que agregue Brave Search y creemos el agente investigador?

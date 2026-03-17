# Investigación: Skills y MCPs para Coordinator

## Contexto

El **Coordinator** es el orquestador principal de Galileo. Recibe tareas del usuario, las analiza, y coordina a los agentes especializados.

## Pregunta
¿Qué **skills** y **MCPs** adicionales serían relevantes para el Coordinator?

---

## Análisis Crítico: ¿Qué necesita el Coordinator?

### Funciones del Coordinator:

| Función | Qué necesita |
|---------|--------------|
| **Analizar tareas** | Capacidad de entender el contexto, hacer preguntas |
| **Planificar** | Metodología para estructurar trabajo |
| **Coordinar** | Comunicación entre agentes |
| **Validar** | Verificar calidad de entregas |
| **Documentar** | Generar reportes, mantener estado |
| **Aprender** | Consultar memoria, guardar aprendizajes |

---

## Skills Relevantes (Investigación)

### Skills Existentes de Superpowers (YA INTEGRADOS)

| Skill | Uso en Coordinator | Estado |
|-------|-------------------|--------|
| brainstorming | Para diseñar soluciones cuando hay ambigüedad | ✅ Ya tenemos |
| writing-plans | Para crear planes de implementación | ✅ Ya tenemos |
| systematic-debugging | Para resolver problemas entre fases | ✅ Ya tenemos |
| test-driven-development | Para cuando agents escriben código | ✅ Ya tenemos |

### Skills Adicionales (ANALIZADOS)

| Skill | Descripción | Relevancia | Recomendación |
|-------|-------------|------------|---------------|
| **skill-creator** | Crear nuevos skills | 🟡 Media | **NO** - El Coordinator no crea skills |
| **doc-coauthoring** | Colaborar en documentos | 🟢 Alta | **AGREGAR** - Para generar specs y reportes |
| **pdf** | Trabajar con PDFs | 🟡 Media | **CONSIDERAR** - Si necesita leer PDFs |
| **xlsx** | Trabajar con Excel | 🟡 Media | **CONSIDERAR** - Si necesita analizar datos |
| **webapp-testing** | Testing de apps | 🔴 Baja | **NO** - No es su responsabilidad |
| **mcp-builder** | Crear MCP servers | 🔴 Baja | **NO** - No es su responsabilidad |
| **brand-guidelines** | Guías de marca | 🔴 Baja | **NO** - No aplica |

### Análisis Crítico: Skills a AGREGAR

| Skill | Justificación |
|-------|---------------|
| **doc-coauthoring** | El Coordinator genera business specs, reportes, estados de proyecto. Necesita crear documentos profesionales. |

---

## MCPs Relevantes (Investigación)

### MCPs YA Configurados

| MCP | Uso en Coordinator | Estado |
|-----|-------------------|--------|
| filesystem | Leer/write archivos del proyecto | ✅ |
| memory | Consultar/grabar memoria | ✅ |
| git | Versionar el código | ✅ |
| sqlite | Guardar estado del proyecto | ✅ |
| fetch | Investigar en web | ✅ |

### MCPs Adicionales ANALIZADOS

| MCP | Descripción | Relevancia | Recomendación |
|-----|-------------|------------|---------------|
| **Brave Search** | Búsqueda web | 🟢 Alta | **AGREGAR** - Para investigar temas cuando recibe tareas |
| **Slack/Discord** | Mensajería | 🟡 Media | **CONSIDERAR** - Para notificar al usuario |
| **Notion** | Base de conocimiento | 🟡 Media | **CONSIDERAR** - Para acceder a documentación |
| **Google Drive** | Archivos | 🔴 Baja | Ya tenemos filesystem |
| **GitHub** | Repo management | 🔴 Baja | Ya tenemos git MCP |
| **Linear/Jira** | Project management | 🟡 Media | **CONSIDERAR** - Para tracking de proyectos |
| **Puppeteer** | Browser automation | 🔴 Baja | No aplica |
| **Sentry** | Monitoring errors | 🔴 Baja | No es su responsabilidad |
| **PostgreSQL** | Base de datos | 🔴 Baja | Ya tenemos SQLite |

### Análisis Crítico: MCPs a AGREGAR

| MCP | Justificación |
|-----|---------------|
| **Brave Search** | El Coordinator recibe tareas que pueden requerir investigación previa. Si el usuario dice "quiero predecir X", el Coordinator debe poder investigar qué es X, mejores prácticas, etc. |

---

## Recomendaciones Finales

### Skills a Agregar

| Skill | Prioridad | Notas |
|-------|-----------|-------|
| doc-coauthoring | 🟡 Media | Para documentos profesionales |

**Mi recomendación: NO agregar ahora.** 
- El Coordinator puede usar las herramientas existentes (filesystem) para crear documentos.
- Los documentos que genera están bien con Markdown simple.
- Agregar más skills lo hace más complejo sin beneficio claro.

### MCPs a Agregar

| MCP | Prioridad | Notas |
|-----|-----------|-------|
| Brave Search | 🟢 Alta | **AGREGAR** - Investigación web |
| Slack | 🟡 Media | Para notificaciones (futuro) |
| Linear/Jira | 🟡 Media | Para tracking (futuro) |

**Mi recomendación: Agregar Brave Search.**
- Permite investigación autónoma
- Whitelist de dominios ya configurado en seguridad
- Útil para la Faceta 2 (Investigación) también

---

## Decisión del Usuario

### Opción A: Solo lo esencial (RECOMENDADO)
```bash
# Sin cambios - el Coordinator funciona bien con lo que tiene
```

### Opción B: Agregar Brave Search
```bash
mcporter config add brave-search "npx -y @modelcontextprotocol/server-brave-search"
```

### Opción C: Agregar Brave Search + Notion
```bash
mcporter config add brave-search "npx -y @modelcontextprotocol/server-brave-search"
mcporter config add notion "npx -y notion-calendar-mcp"
```

---

## Mi Análisis Crítico

### ¿Por qué no agregar más skills?

1. **El Coordinator ya tiene lo necesario:**
   - brainstorming → para diseñar cuando hay ambigüedad
   - systematic-debugging → para resolver problemas
   - filesystem → para crear documentos

2. **Más skills = más complejidad:**
   - Cada skill requiere contexto adicional
   - Puede ralentizar al agente
   - Beneficio marginal para su función

### ¿Por qué sí agregar Brave Search?

1. **Investigación es parte de su trabajo:**
   - Cuando llega una tarea nueva, debe poder investigar
   - "Quiero predecir churn" → investigar qué es churn, mejores prácticas
   - "Quiero hacer un chatbot" → investigar frameworks

2. **Seguridad ya está configurada:**
   - Solo permite dominios de documentación técnica
   - No puede acceder a localhost ni redes privadas

3. **Beneficio para Faceta 2:**
   - La Faceta 2 (Investigación) también usará búsqueda
   - Un solo MCP sirve para múltiples propósitos

---

## Conclusión

| Componente | Recomendación |
|------------|--------------|
| **Skills** | ✅ No agregar más (los actuales son suficientes) |
| **MCPs** | 🟡 Agregar Brave Search (investigación web) |

**Veredicto:** Agregar **Brave Search MCP** para investigación. Los skills actuales son suficientes.

---

## Acción Sugerida

```bash
# Agregar Brave Search
mcporter config add brave-search "npx -y @modelcontextprotocol/server-brave-search"
```

¿Quieres que lo agregue?

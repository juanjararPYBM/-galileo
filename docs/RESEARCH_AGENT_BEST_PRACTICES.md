# Investigación: Mejores Prácticas para Agentes de Investigación

## Fuentes Consultadas

| Fuente | Tipo | Relevancia |
|--------|------|------------|
| DeerFlow (ByteDance) | Framework | 🟢 Alta - SuperAgent para investigación |
| AutoGen (Microsoft) | Framework | 🟢 Alta - Multi-agent |
| LangChain | Framework | 🟡 Media - Herramientas |

---

## Hallazgos: Patrones Recomendados

### 1. Estructura de Agentes de Investigación

DeerFlow y AutoGen usan una estructura similar:

```
Research Agent
    │
    ├── Planning Agent    → Define estrategia de investigación
    ├── Search Agent     → Busca información
    ├── Extraction Agent → Extrae datos
    ├── Analysis Agent   → Analiza hallazgos
    └── Synthesis Agent  → Genera reporte
```

**Nuestro enfoque actual (Galileo):**
- ✅ Research Agent (análisis + síntesis)
- ✅ Data Collector Agent (extracción)
- ✅ Diferentes agentes para diferentes tareas

**Mejora propuesta:** Dividir en subagentes especializados

---

## 2. Técnicas de Búsqueda Recomendadas

### Búsqueda Multi-Fuente
| Técnica | Descripción | Implementar? |
|---------|-------------|--------------|
| **Parallel Search** | Buscar en múltiples fuentes simultáneamente | ✅ SÍ |
| **Iterative Refinement** | Refinar búsqueda basada en resultados | ✅ SÍ |
| **Cross-Reference** | Verificar información con múltiples fuentes | ✅ SÍ |
| **Semantic Search** | Buscar por significado (Exa) | ✅ YA TENEMOS |

### Depth-First vs Breadth-First
| Enfoque | Cuándo Usar |
|---------|--------------|
| **Depth-First** | Tema específico, necesita detalle |
| **Breadth-First** | Tema amplio, necesita overview |

---

## 3. Validación de Información

### Técnicas de Verificación
| Técnica | Descripción |
|---------|-------------|
| **Cross-referencing** | Verificar con 2+ fuentes independientes |
| **Authority Check** | Priorizar fuentes académicas/oficiales |
| **Date Check** | Verificar que información está actualizada |
| **Bias Detection** | Identificar posibles sesgos |

### Nuestro Sistema
- ✅ Cross-referencing: Pendiente implementar
- ✅ Authority Check: En whitelist de dominios
- ✅ Date Check: En metadata
- ✅ Bias Detection: Pendiente

---

## 4. Extracción de Datos

### Técnicas Recomendadas (DeerFlow)
| Técnica | Descripción | Nuestro MCP |
|---------|-------------|-------------|
| **HTML to Markdown** | Convertir web a texto limpio | ✅ Fetch |
| **Structured Extraction** | Extraer datos estructurados | ✅ Firecrawl |
| **Table Extraction** | Extraer tablas | ✅ Firecrawl |
| **PDF Parsing** | Extraer de PDFs | 🔄 Agregar |

### Mejora Propuesta: Agregar PDF MCP
```bash
# MCP para PDFs
mcporter config add pdf "npx -y @modelcontextprotocol/server-pdf"
```

---

## 5. Memoria y Contexto

### Técnicas de Long-Term Memory (DeerFlow)
| Técnica | Descripción | Nuestro Estado |
|---------|-------------|----------------|
| **Entity Memory** | Recordar entidades vistas | ✅ Memory MCP |
| **Search History** | Evitar búsquedas duplicadas | 🔄 Implementar |
| **Learn from Feedback** | Mejorar basado en correcciones | 🔄 Implementar |

---

## 6. Seguridad en Investigación

### De AutoGen - Warnings de Seguridad
```
⚠️ "Only connect to trusted MCP servers as they may execute commands
in your local environment or expose sensitive information."
```

### Nuestro Enfoque ✅
- ✅ Whitelist de dominios
- ✅ Validación de URLs
- ✅ Detección de prompt injection
- ✅ Sanitización de contenido

---

## 7. Workflows de Investigación

### Patrón Recomendado (DeerFlow)
```
1. Clarify Task     → Entender exactamente qué investigar
2. Plan Search     → Definir fuentes y estrategia
3. Execute Search  → Buscar en paralelo
4. Extract         → Extraer información relevante
5. Validate        → Verificar con fuentes adicionales
6. Synthesize      → Generar reporte final
7. Store Memory    → Guardar para referencia futura
```

### Nuestro Workflow Actual
```
1. Research Agent recibe tarea
2. Define preguntas de investigación
3. Busca con brave-search, exa, fetch
4. Data Collector extrae datos (si necesita)
5. Security valida contenido
6. Synthesiza en reporte
7. Guarda en memoria
```

**Comparación:** Nuestro workflow es similar ✅

---

## 8. Herramientas y Extensiones Recomendadas

### MCPs Adicionales a Considerar

| MCP | Propósito | Prioridad |
|-----|-----------|-----------|
| **Playwright** | Web automation | 🟡 Media |
| **PDF Parser** | Leer PDFs | 🟡 Media |
| **YouTube** | Transcribir videos | 🟡 Media |
| **Notion** | Guardar en base de conocimiento | 🟡 Media |

---

## 9. Mejores Prácticas: Calidad de Investigación

### De la Comunidad

| Práctica | Descripción |
|----------|-------------|
| **Tres fuentes mínimo** | Siempre verificar con ≥3 fuentes |
| **Priorizar académicas** | ArXiv, papers > blogs > general |
| **Fecha de publicación** | Verificar que no esté obsoleto |
| **Leer originales** | No confiar solo en resúmenes |
| **Documentar todo** | Fuentes, fechas, autores |

### Métricas de Calidad

| Métrica | Target |
|---------|--------|
| Fuentes por hecho | ≥ 3 |
| Fuentes académicas | ≥ 30% |
| Tiempo de investigación | < 30 min |
| Verificación de fecha | 100% |

---

## 10. Integración con Other Facetas

### Con Data Science (CRISP-DM)
```
Data Science Project
    │
    ├── Fase 1: Business → Research Agent
    │    └→ Investiga dominio, competidores
    │
    ├── Fase 2: Data → Research Agent
    │    └→ Benchmarks, datasets disponibles
    │
    └── Fase 4: Modeling → Research Agent
         └→ Técnicas state-of-the-art
```

### Con Coordinator
```
Coordinator recibe tarea
    │
    ├─→ ¿Requiere investigación?
    │       │
    │      Sí → Research Agent
    │              │
    │              └→ ¿Requiere datos?
    │                      │
    │                     Sí → Data Collector
    │
    └─→ No → Continúa normal
```

---

## Análisis Crítico: ¿Qué Nos Falta?

### Lo que YA tenemos ✅
- Research Agent (análisis)
- Data Collector Agent (extracción)
- Brave Search, Exa, Firecrawl, Fetch
- Seguridad completa
- Memoria jerárquica

### Lo que PODRÍAMOS agregar

| Componente | Justificación | Prioridad |
|------------|--------------|-----------|
| **Subagentes** | Mayor especialización | 🟡 Media |
| **PDF Parser** | Papers académicos | 🟡 Media |
| **Cross-referencing** | Verificación automática | 🟡 Media |
| **Search History** | Evitar duplicados | 🔴 Baja |
| **Playwright** | Web automation | 🔴 Baja |

---

## Recomendaciones Finales

### Inmediato (Ahora)
- ✅ Mantener lo que tenemos
- ✅ Usar los 3 MCPs de búsqueda (brave, exa, firecrawl)

### Corto Plazo (Esta semana)
- Agregar validación cross-reference (verificar con múltiples fuentes)
- Agregar PDF parser si necesitamos papers académicos

### Largo Plazo (Próximo mes)
- Considerar subagentes si la investigación se vuelve compleja
- Evaluar necesidad de Notion para base de conocimiento

---

## Decisión

### Lo que tenemos AHORA es SUFICIENTE para un inicio sólido:

| Capacidad | Estado |
|-----------|--------|
| Búsqueda web | ✅ 3 MCPs |
| Extracción de datos | ✅ Firecrawl |
| Seguridad | ✅ Completa |
| Memoria | ✅ Jerárquica |
| Análisis | ✅ Research Agent |

**No necesitamos agregar más por ahora.** Podemos comenzar a usar y refinar basado en experiencia.

---

## Acción Sugerida

```bash
# Solo si necesitamos PDFs académicos:
# mcporter config add pdf-parser "npx -y @modelcontextprotocol/server-pdf"
```

**Veredicto:** Comenzar a usar la Faceta 2 con lo que tenemos. Agregar más solo cuando la experiencia lo requiera.

---

## Pregunta al Usuario

¿Querés que:
1. **Comencemos a usar** la Faceta 2 con lo que tenemos?
2. **Agreguemos PDF parser** para papers académicos?
3. **Diseñemos subagentes** de investigación más especializados?

¿Qué preferís?

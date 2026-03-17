# GALILEO - Ecosistema de Agentes Genérico

## Visión

> **Disectar cualquier tarea en partes lógicas, asignar agentes especializados, aprender de cada ejecución.**

Galileo es un sistema generalize para resolver **cualquier tipo de tarea** usando:
1. Una LLM económica y de alto rendimiento (MiniMax)
2. Descomposición de tareas en componentes lógicos
3. Agentes especializados por tipo de componente
4. Memoria que aprende y refina habilidades
5. Seguridad integrada

---

## Arquitectura General

```
                    ┌─────────────────┐
                    │   COORDINATOR   │
                    │   (Galileo)     │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   FACETA 1      │ │   FACETA 2      │ │   FACETA N      │
│   CRISP-DM      │ │   INVESTIGACIÓN │ │   [Próxima]     │
│   (Data Science)│ │                 │ │                 │
└────────┬────────┘ └────────┬────────┘ └─────────────────┘
         │                   │
    ┌────┴────┐         ┌────┴────┐
    │         │         │         │
    ▼         ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│Agentes│ │Agentes│ │Research│ │ Data  │
│  DS   │ │  DS   │ │ Agent │ │Collector│
└───────┘ └───────┘ └───────┘ └───────┘
```

---

## Estado: FACETAS COMPLETAS

### ✅ Faceta 1: Data Science (CRISP-DM)
- 7 agentes especializados por fase

### ✅ Faceta 2: Investigación
- Research Agent
- Data Collector Agent
- 11 MCPs configurados

---

## Faceta 1: Data Science (CRISP-DM) ✅ COMPLETA

| Fase | Agente | Responsabilidad |
|------|--------|-----------------|
| 1 | Business Agent | Objetivos de negocio |
| 2 | Data Explorer Agent | Exploración de datos |
| 3 | Data Engineer Agent | Preparación y limpieza |
| 4 | ML Engineer Agent | Modelado y entrenamiento |
| 5 | Evaluation Agent | Evaluación y validación |
| 6 | MLOps Agent | Despliegue a producción |

---

## Faceta 2: Investigación ✅ COMPLETA

### Agentes
| Agente | Responsabilidad |
|--------|-----------------|
| Research Agent | Analiza, sintetiza, conclusiones |
| Data Collector Agent | Extrae datos con seguridad |

### MCPs Configurados
| MCP | Función |
|-----|---------|
| brave-search | Búsqueda web |
| exa-search | Búsqueda semántica |
| firecrawl | Scraping avanzado |
| fetch | Obtener páginas |
| pdf-parser | Leer PDFs |
| playwright | Web automation |
| notion | Base de conocimiento |

---

## Sistema de Memoria

### Tres Niveles de Aprendizaje

```
┌────────────────────────────────────────────────────┐
│                   MEMORIA GLOBAL                    │
│   Errores y patrones que aplican a TODAS las       │
│   facetas y tareas                                  │
└────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────┐
│               MEMORIA POR FACETA                   │
│   Errores y patrones específicos de cada tipo     │
│   de tarea (Data Science, Investigación, etc.)     │
└────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────┐
│             MEMORIA POR PROYECTO                  │
│   Lecciones específicas de este proyecto          │
└────────────────────────────────────────────────────┘
```

---

## Agentes Base

### Coordinator
- Analiza tareas entrantes
- Determina tipo de tarea
- Disecta en partes lógicas
- Asigna a agentes apropiados

### Security Agent
- Audita todas las operaciones
- Previene ataques
- Protege datos
- Valida configuraciones

### Memoria System
- Registra aprendizajes
- Consulta antes de actuar
- Refina patrones automáticamente

---

## Diferenciación

| Característica | Otros Sistemas | GALILEO |
|----------------|----------------|---------|
| Propósito | Específico | **Genérico** |
| LLM | Variable | **MiniMax** |
| Metodología | Fija | **Disección adaptable** |
| Memoria | No / Simple | **Jerárquica 3 niveles** |
| Seguridad | Opcional | **Integrada** |
| Extensible | Limitado | **Facetas ilimitadas** |

---

## Roadmap de Facetas

- [x] Faceta 1: Data Science (CRISP-DM)
- [x] Faceta 2: Investigación
- [ ] Faceta 3: Desarrollo de Software
- [ ] Faceta 4: Automatización
- [ ] ... (extendible)

---

## Principios de Diseño

1. **Modular** - Cada faceta es independiente
2. **Aprendizaje continuo** - Memoria jerárquica
3. **Especialización** - Agentes expertos por área
4. **Seguridad primero** - Security Agent siempre activo
5. **Economía** - MiniMax para máximo rendimiento/costo
6. **Extensibilidad** - Nuevas facetas fácil de agregar

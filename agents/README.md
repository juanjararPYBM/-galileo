# CRISP-DM Agent Ecosystem

## Arquitectura

```
                    ┌─────────────────┐
                    │   Coordinator   │
                    │    (Main)       │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Business      │ │    Data         │ │    Data         │
│   Agent         │ │    Explorer     │ │    Engineer     │
│   (Phase 1)     │ │    Agent        │ │    Agent        │
│                 │ │    (Phase 2)    │ │    (Phase 3)    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    ML Engineer   │
                    │    Agent        │
                    │    (Phase 4)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Evaluation    │
                    │    Agent        │
                    │    (Phase 5)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    MLOps        │
                    │    Agent        │
                    │    (Phase 6)    │
                    └─────────────────┘
```

## Agentes

| Agente | Fase | Rol | Entregable |
|--------|------|-----|------------|
| **Coordinator** | - | Orchestrator | Project state |
| **Business Agent** | 1 | Objetivos de negocio | business-spec.md |
| **Data Explorer Agent** | 2 | Exploración de datos | data-profile.md |
| **Data Engineer Agent** | 3 | Preparación de datos | prepared-dataset/ |
| **ML Engineer Agent** | 4 | Entrenamiento | trained-model/ |
| **Evaluation Agent** | 5 | Validación | evaluation-report.md |
| **MLOps Agent** | 6 | Deployment | production-service/ |

## Estructura

```
agents/
├── coordinator/
│   └── SYSTEM.md           # Orchestrator principal
└── phases/
    ├── business-agent/
    │   └── SYSTEM.md       # Fase 1: Business Understanding
    ├── data-explorer-agent/
    │   └── SYSTEM.md       # Fase 2: Data Understanding
    ├── data-engineer-agent/
    │   └── SYSTEM.md       # Fase 3: Data Preparation
    ├── ml-engineer-agent/
    │   └── SYSTEM.md       # Fase 4: Modeling
    ├── evaluation-agent/
    │   └── SYSTEM.md       # Fase 5: Evaluation
    └── mlops-agent/
        └── SYSTEM.md       # Fase 6: Deployment
```

## Skills Disponibles

Los agentes también tienen acceso a las skills de Superpowers:

| Skill | Uso |
|-------|-----|
| brainstorming | Diseño inicial |
| writing-plans | Planes de implementación |
| subagent-driven-development | Ejecución con subagentes |
| test-driven-development | Metodología TDD |
| systematic-debugging | Debugging estructurado |

## Uso

### Iniciar un Proyecto

```
Usuario: "Quiero predecir churn de clientes"

Coordinator recibe la tarea → Business Agent inicia → fases sucesivas
```

### Flujo Típico

1. **Usuario** describe problema de negocio
2. **Coordinator** analiza y planifica fases
3. **Business Agent** define objetivos y métricas
4. **Data Explorer Agent** explora datos disponibles
5. **Data Engineer Agent** prepara dataset
6. **ML Engineer Agent** entrena modelo
7. **Evaluation Agent** valida contra negocio
8. **MLOps Agent** despliega a producción

### Comandos

| Comando | Acción |
|---------|--------|
| `/start <proyecto>` | Iniciar nuevo proyecto |
| `/status` | Ver estado actual |
| `/phase <n>` | Ir a fase específica |
| `/report` | Generar reporte |

## Integración con OpenClaw

Estos agentes pueden invocarse como subagentes desde la sesión principal:

```python
# Ejemplo de invocación
sessions_spawn(
    agent="data-explorer-agent",
    task="Explorar datos del proyecto churn",
    runtime="subagent"
)
```

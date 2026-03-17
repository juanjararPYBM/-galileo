# Sistema de Memoria para Agentes CRISP-DM

## Propósito

Cada vez que un agente completa una tarea, registra lo que funcionó y lo que no. Los agentes pueden consultar esta memoria antes de actuar para evitar errores pasados.

## Estructura de Memoria

```
memory/
├── lessons/
│   ├── YYYY-MM-DD.md          # Lecciones diarias
│   └── ...
├── patterns/
│   ├── successful-patterns.md # Qué funciona
│   └── failure-patterns.md    # Qué falló
├── agents/
│   ├── business-agent/
│   │   └── history.md
│   ├── data-explorer-agent/
│   ├── ml-engineer-agent/
│   └── ...
└── projects/
    └── <project-name>/
        └── learnings.md
```

## Formato de Lecciones

### Después de cada fase (agente completa tarea):

```markdown
# Lesson: <Proyecto> - <Fase>
Date: YYYY-MM-DD
Agent: <agent-name>
Phase: <phase-number>

## ✅ Qué funcionó
- [Punto 1]
- [Punto 2]

## ❌ Qué falló
- [Punto 1]
- [Reason] → [Lección]

## 🔧 Corrección aplicada
- [Cómo se arregló]

## 📚 Para próxima vez
- [Recomendación]
```

### Ejemplo real:

```markdown
# Lesson: Churn Prediction - Data Preparation
Date: 2026-03-16
Agent: data-engineer-agent
Phase: 3

## ✅ Qué funcionó
- Pipeline de limpieza automatizado funcionó bien
- Target encoding para categorías de alta cardinalidad

## ❌ Qué falló
- Imputación con media distorsionó distribución de age
- Reason: Los outliers influían mucho → Lección: Usar mediana o RobustScaler

## 🔧 Corrección aplicada
- Cambiamos a imputación con mediana
- Agregamos missing_indicator column

## 📚 Para próxima vez
- Siempre verificar distribución después de imputar
- Probar múltiples estrategias de imputación antes de decidir
```

## Consulta de Memoria (Antes de actuar)

Cada agente DEBE consultar la memoria antes de:

1. **Elegir estrategia de limpieza**
2. **Seleccionar algoritmo**
3. **Definir métricas**
4. **Diseñar pipeline**

### Template de consulta:

```python
# El agente ejecuta esto antes de decidir
def consult_memory(agent_name, phase, context):
    # 1. Buscar lecciones similares
    lessons = search_lessons(
        agent=agent_name,
        phase=phase,
        keywords=context
    )
    
    # 2. Mostrar advertencias relevantes
    for lesson in lessons['failures']:
        if matches_context(lesson, context):
            warning(f"PREVIAMENTE FALLÓ: {lesson.description}")
    
    # 3. Mostrar patrones exitosos
    for pattern in lessons['successes']:
        if matches_context(pattern, context):
            info(f"PREVIAMENTE FUNCIONÓ: {pattern.description}")
```

## Index Automático

Después de cada lesson, actualizar el índice:

```markdown
# Pattern Index

## Data Preparation Failures
| Problema | Frecuencia | Solución |
|----------|------------|----------|
| Imputación con media | 3x | Usar mediana |
| Missing > 20% sin flag | 2x | Agregar indicador |

## Modeling Successes
| Patrón | Veces | Notas |
|---------|-------|-------|
| XGBoost para tabular | 5x | Mejor recall |
| Baseline LogReg | 7x | Siempre empezar |
```

## Uso en Agentes

### Al inicio de cada fase:

```
[Agent] consultando memoria para <fase>...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 Patrones exitosos relacionados:
- "XGBoost para datos desbalanceados" (3 proyectos)
- "Target encoding para alta cardinalidad"

⚠️ Errores previos relacionados:
- "No verificar distribución post-imputación" (2x)
- "Olvidar stratified split para clases desbalanceadas"

→ Aplicando recomendaciones de memoria...
```

### Después de completar fase:

```
[Agent] guardando lección...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Registrado: <proyecto>-<fase>.md
📚 Actualizado: patterns/successful-patterns.md
📚 Actualizado: patterns/failure-patterns.md
```

## Búsqueda Semántica

La memoria usa búsqueda semántica para encontrar lecciones relevantes:

- Buscar por: fase, tipo de problema, algoritmo, tipo de dato
- Matching con contexto actual del agente

## Mantenimiento

- **Semanal**: Revisar lessons accumulateadas, consolidar patrones
- **Mensual**: Actualizar patterns/ con insights refinados
- **Por proyecto**: Crear proyecto específico en projects/

---

## Regla de Oro

> **No repetir errores dos veces.**
> Si algo falló, documentar para que ningún agente lo vuelva a hacer.

# Sistema de Memoria Jerárquico para Agentes

## Estructura de Memoria

```
memory/
├── global/                          # 🌍 Memoria GLOBAL (todos los proyectos)
│   ├── lessons/                     # Lecciones aplicables a cualquier proyecto
│   ├── patterns/
│   │   ├── successful.md            # Patrones que siempre funcionan
│   │   └── failures.md              # Errores a evitar siempre
│   └── index.md                     # Índice de lecciones globales
│
├── types/                           # 📂 Memoria por TIPO DE PROYECTO
│   ├── classification/              # Proyectos de clasificación
│   │   ├── lessons/
│   │   └── patterns/
│   ├── regression/                 # Proyectos de regresión
│   │   ├── lessons/
│   │   └── patterns/
│   ├── nlp/                        # Proyectos de NLP
│   ├── time-series/                # Proyectos de series temporales
│   ├── computer-vision/            # Proyectos de visión por computador
│   └── clustering/                 # Proyectos de clustering
│
└── projects/                       # 📁 Memoria por PROYECTO ESPECÍFICO
    └── <nombre-proyecto>/
        ├── lessons/
        ├── patterns/
        ├── artifacts/               # Modelos, datasets guardados
        └── learnings.md             # Resumen de aprendizajes
```

---

## Niveles de Memoria

### Nivel 1: Global 🌍

**¿Qué guarda?** Errores y patrones que aplican a **cualquier** proyecto DS/ML.

**Ejemplos:**
```markdown
# GLOBAL: Errores a Evitar

## Siempre
- [ ] No hacer test/train split antes de feature engineering
- [ ] No usar datos de test para validación durante entrenamiento
- [ ] No eliminar outliers sin investigarlos primero
- [ ] No elegir métricas sin alinear con negocio

## Debugging
- [ ] Siempre verificar distribución de datos
- [ ] Siempre verificar tipos de datos
- [ ] Siempre verificar valores nulos
```

### Nivel 2: Por Tipo de Proyecto 📂

**¿Qué guarda?** Errores específicos de cada tipo de problema.

**Ejemplos para classification:**
```markdown
# TYPE: Classification - Errores Específicos

## Errores Comunes
- [ ] No verificar balance de clases antes de entrenar
- [ ] Usar accuracy con clases desbalanceadas
- [ ] No threshold tuning para producción
- [ ] No analizar falsos positivos vs falsos negativos

## Métricas a Usar
- Precision, Recall, F1 (no solo accuracy)
- ROC-AUC para todas las clases
- PR-AUC para clases desbalanceadas
```

**Ejemplos para time-series:**
```markdown
# TYPE: Time Series - Errores Específicos

## Errores Comunes
- [ ] Hacer shuffle en train/test split (rompe temporalidad)
- [ ] No verificar stationarity
- [ ] No manejar seasonality
- [ ] Data leakage por features future-dependent

## Lo que Funciona
- [ ] Time-based split (no random)
- [ ] Feature: lag variables
- [ ] Verificar stationarity con ADF test
```

### Nivel 3: Por Proyecto 📁

**¿Qué guarda?** Lecciones específicas de un proyecto particular.

```markdown
# PROJECT: Churn Prediction - Lessons

## Fase 2: Data Understanding
- ✅ Identificamos 15% de valores nulos en 'tenure'
- ❌ NO-investigamos la razón de los nulos → problema en Fase 3

## Fase 3: Data Preparation
- ❌ Imputación con media distorsionó distribución
- ✅ Corrección: mediana + missing_indicator
- 📚 Para próximo proyecto: siempre verificar distribución post-imputación

## Fase 4: Modeling
- ✅ XGBoost outperformeó Random Forest (recall 82% vs 75%)
- ❌ No probamos class_weight='balanced' → próximo proyecto sí
```

---

## Cómo Consultar la Memoria

### Antes de cada decisión, el agente consulta:

```
┌─────────────────────────────────────────────────────────────┐
│  CONSULTANDO MEMORIA...                                     │
├─────────────────────────────────────────────────────────────┤
│  Nivel: GLOBAL                                              │
│  ├─ ❌ "No usar accuracy con clases desbalanceadas"        │
│  ├─ ❌ "Siempre hacer EDA antes de feature engineering"    │
│  └─ ✅ "XGBoost funciona bien en datos tabulares"           │
│                                                             │
│  Nivel: TYPE (classification)                               │
│  ├─ ❌ "Verificar balance de clases antes de entrenar"     │
│  ├─ ❌ "Hacer threshold tuning para producción"            │
│  └─ ✅ "Usar class_weight para desbalance"                 │
│                                                             │
│  Nivel: PROJECT (churn-prediction)                         │
│  ├─ ❌ "Imputación con media falló → usar mediana"         │
│  └─ ✅ "XGBoost fue el mejor modelo"                        │
└─────────────────────────────────────────────────────────────┘
```

### Template de Consulta

```python
def consultar_memoria(agente, fase, tipo_proyecto, contexto):
    # 1. Consultar global
    lecciones_globales = buscar_en("memory/global", contexto)
    
    # 2. Consultar por tipo
    lecciones_tipo = buscar_en(f"memory/types/{tipo_proyecto}", contexto)
    
    # 3. Consultar proyecto específico
    lecciones_proyecto = buscar_en("memory/projects/proyecto_actual", contexto)
    
    # 4. Unir y presentar (prioridad: proyecto > tipo > global)
    return prioritizar(lecciones_proyecto, lecciones_tipo, lecciones_globales)
```

---

## Cómo Registrar Lecciones

### Después de completar una fase:

```markdown
# Lesson: <Proyecto> - <Fase>
Date: YYYY-MM-DD
Agent: <agent-name>
Phase: <phase-number>
Scope: [global|type|project]

## ✅ Qué funcionó
- [Punto]

## ❌ Qué falló
- [Punto]
- [Causa] → [Lección]

## 📚 Alcance
- [ ] Global (aplica a todos los proyectos)
- [ ] Type: <clasification|nlp|etc> (aplica a este tipo)
- [ ] Project: <nombre> (aplica solo a este proyecto)
```

---

## Regla de Tres Niveles

| Alcance | Cuándo Usar | Ejemplo |
|---------|-------------|---------|
| **Global** | Error que aplica a **cualquier** proyecto ML | "No hacer leakage de datos" |
| **Tipo** | Error específico de un **tipo de problema** | "No usar accuracy en classes desbalanceadas" |
| **Proyecto** | Error solo en **este proyecto específico** | "La columna X tiene 40% nulos" |

---

## Mantenimiento

- **Cada lesson** → clasificar en el nivel correcto
- **Mensual** → revisar lessons acumuladas, promover a nivel superior si aplica
- **Trimestral** → actualizar index de patterns globales

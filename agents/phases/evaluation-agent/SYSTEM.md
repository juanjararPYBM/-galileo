# Agente: Evaluation Agent
## Fase: 5 - Evaluation (CRISP-DM)

## Rol
Especialista en evaluación de modelos contra objetivos de negocio. Determina si el modelo está listo para producción.

## Objetivo
Validar que el modelo cumple los criterios de éxito de negocio y es viable para deployment.

## Dependencias
- **Entrada**: Trained Model + Business Spec + Data Profile
- **Salida**: Evaluation Report + Go/No-Go Decision

---

## Proceso de Trabajo

### Paso 1: Evaluación Técnica

**Métricas de clasificación:**

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score,
    confusion_matrix, classification_report
)

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

results = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred),
    'recall': recall_score(y_test, y_pred),
    'f1': f1_score(y_test, y_test),
    'roc_auc': roc_auc_score(y_test, y_pred_proba),
    'pr_auc': average_precision_score(y_test, y_pred_proba)
}
```

**Matriz de confusión:**

```python
cm = confusion_matrix(y_test, y_pred)
# cm[0,0] = TN (True Negatives)
# cm[0,1] = FP (False Positives)  
# cm[1,0] = FN (False Negatives)
# cm[1,1] = TP (True Positives)

# Calcular métricas adicionales
tn, fp, fn, tp = cm.ravel()
specificity = tn / (tn + fp)
```

### Paso 2: Evaluación por Segmento

**Analizar performance por grupos:**

```python
# Por segmento demográfico
for segment in df_test['segment'].unique():
    mask = df_test['segment'] == segment
    segment_metrics = {
        'recall': recall_score(y_test[mask], y_pred[mask]),
        'precision': precision_score(y_test[mask], y_pred[mask])
    }
    print(f"Segment {segment}: {segment_metrics}")
```

**Verificar equity:**

| Segmento | Recall | Precision | Disparidad |
|----------|--------|-----------|------------|
| Grupo A | 0.85 | 0.70 | baseline |
| Grupo B | 0.82 | 0.72 | -3% recall |
| Grupo C | 0.78 | 0.68 | -7% recall ⚠️ |

### Paso 3: Análisis de Errores

**¿Qué tipo de errores comete el modelo?**

```python
# Identificar patrones en errores
errors = y_test != y_pred
error_df = df_test[errors].copy()
error_df['predicted'] = y_pred[errors]
error_df['actual'] = y_test[errors]

# Análisis: ¿son aleatorios o tienen patrón?
print("Errores por hora del día:")
print(error_df['hour'].value_counts())
```

**Tipos de error y su impacto:**

| Error Type | Descripción | Impacto de Negocio |
|------------|-------------|-------------------|
| FP (False Positive) | Predice sí, realidad no | Costo de acción innecesaria |
| FN (False Negative) | Predice no, realidad sí | Perdida oportunidad |

### Paso 4: Análisis de Robustez

**¿Qué pasa si cambia la distribución?**

```python
# Simular slight distribution shift
X_test_shifted = X_test.copy()
X_test_shifted['feature_1'] *= 1.1  # 10% increase
X_test_shifted['feature_2'] *= 0.9  # 10% decrease

# Evaluar en datos "shifted"
y_pred_shifted = model.predict(X_test_shifted)
metrics_shifted = recall_score(y_test, y_pred_shifted)

print(f"Original Recall: {original_recall:.3f}")
print(f"Shifted Recall: {metrics_shifted:.3f}")
print(f"Degradation: {(original_recall - metrics_shifted):.3f}")
```

### Paso 5: Validación contra Business Spec

**Mapear métricas técnicas a de negocio:**

| Métrica Técnica | Target | Encontrado | Negocio Impact |
|-----------------|--------|------------|----------------|
| Recall | >80% | 82% | ✅ Atendemos 82% de churners |
| Precision | >60% | 65% | ✅ 65% de predicciones son correctas |
| Latencia | <100ms | 45ms | ✅足够 rápido |

**Verificar todos los criterios:**

```markdown
## Criterios de Éxito (from Business Spec)
- [✅] Recall > 80%: 82%
- [✅] Precision > 60%: 65%
- [✅] AUC > 75%: 86%
- [✅] Latencia P95 < 100ms: 45ms
- [✅] Costo por predicción < $0.01: $0.002
```

### Paso 6: Análisis de Bias/Fairness

**Verificar equity:**

```python
# Por grupo protegido (si aplica)
protected_groups = ['gender', 'age_group', 'region']

for group in protected_groups:
    for value in df_test[group].unique():
        mask = df_test[group] == value
        recall = recall_score(y_test[mask], y_pred[mask])
        print(f"{group}={value}: recall={recall:.3f}")
```

**Reporte de fairness:**

| Grupo | Recall | Precision | Notas |
|-------|--------|-----------|-------|
| Male | 0.83 | 0.66 | OK |
| Female | 0.81 | 0.64 | OK |
| Diferencia | 2% | 2% | Aceptable |

### Paso 7: Decisión Go/No-Go

**Matriz de decisión:**

| Criterio | Threshold | Resultado | ¿Bloqueante? |
|----------|-----------|-----------|--------------|
| Recall vs Target | >80% | 82% ✅ | No |
| Precision vs Target | >60% | 65% ✅ | No |
| AUC vs Target | >75% | 86% ✅ | No |
| Latencia vs Target | <100ms | 45ms ✅ | No |
| Bias entre grupos | <10% | 5% ✅ | No |
| Estabilidad | <5% drop | 3% ✅ | No |

**Decisión:**

```
✅ GO - El modelo cumple todos los criterios de éxito
```

**O** 

```
❌ NO-GO - El modelo no cumple los criterios mínimos
- Recall: 72% (target: 80%) - Bloqueante
- Recomendación: Regresar a Modeling con más datos
```

---

## Output: Evaluation Report

El agente DEBE generar: `docs/projects/<project-name>/evaluation.md`

```markdown
# Evaluation: <Proyecto>

## Resumen Ejecutivo
El modelo [nombre] [cumple/no cumple] los criterios de éxito definidos.

## Evaluación Técnica

### Métricas en Test Set
| Métrica | Target | Actual | Delta |
|---------|--------|--------|-------|
| Recall | >80% | 82% | +2% |
| Precision | >60% | 65% | +5% |
| F1 | >65% | 72% | +7% |
| AUC | >75% | 86% | +11% |
| Latencia | <100ms | 45ms | OK |

### Matriz de Confusión
|  | Pred: No | Pred: Sí |
|--|----------|----------|
| Actual: No | TN=850 | FP=150 |
| Actual: Sí | FN=180 | TP=820 |

- TP: 820 (churners correctly identified)
- TN: 850 (non-churners correctly identified)
- FP: 150 (false alarms - cost: $X)
- FN: 180 (missed churners - cost: $Y)

## Evaluación por Segmento
| Segmento | Recall | Precision | Notas |
|----------|--------|-----------|-------|
| Segment A | 85% | 68% | OK |
| Segment B | 79% | 62% | OK |
| Segment C | 80% | 64% | OK |

## Análisis de Errores
### Patrones en Falsos Negativos (churners no detectados)
1. 40% tienen tenure < 3 meses (usuarios nuevos)
2. 25% tienen contrato mensual
3. 20% no tienen support tickets

### Patrones en Falsos Positives (falsos alarmass)
1. 30% tienen alta actividad reciente
2. 25% cambiaron de plan recientemente

## Análisis de Bias
| Grupo | Recall | Disparidad |
|-------|--------|-------------|
| Male | 83% | baseline |
| Female | 81% | -2% |
| 18-30 | 80% | baseline |
| 31-50 | 84% | +4% |
| 51+ | 79% | -1% |

**Conclusión:** No hay bias significativo (>10%)

## Robustez
- 10% distribution shift: Recall drops 3% (aceptable)
- 20% distribution shift: Recall drops 8% (investigación needed)

## Validación contra Business Spec
| Objetivo | Métrica | Target | Actual | Status |
|----------|---------|--------|--------|--------|
| Reducir churn | Recall | >80% | 82% | ✅ |
| Reducir churn | Precision | >60% | 65% | ✅ |
| Eficiencia | Latencia | <100ms | 45ms | ✅ |

## Decisión

### ✅ GO
- [x] Cumple criterios técnicos
- [x] Cumple criterios de negocio
- [x] No hay bias significativo
- [x] Robustez aceptable

### Condiciones
- Monitorear recall en producción
- Revisar falsos negativos en Segment C

## Recomendaciones para Production
1. Implementar monitoreo de distribución
2. Revisar modelo si recall baja de 75%
3. Re-entrenar con datos frescos trimestralmente

## Siguiente Fase
- Listo para → **Deployment**
```

---

## Herramientas/Skills Disponibles

- Python (sklearn, matplotlib)
- superpowers:systematic-debugging
- Análisis estadístico

## Reglas

1. **VALIDAR CONTRA BUSINESS SPEC** - No solo métricas genéricas
2. **DOCUMENTAR ERRORES** - Entender qué falla
3. **CHECAR BIAS** - Siempre verificar equity
4. **SER HONESTO** - Si no cumple, decir NO-GO

## Criteria de Calidad

✅ Entregable completo:
- [ ] Métricas técnicas calculadas
- [ ] Análisis por segmento
- [ ] Análisis de errores
- [ ] Validación contra Business Spec
- [ ] Análisis de bias
- [ ] Decisión Go/No-Go clara
- [ ] Documentación completa

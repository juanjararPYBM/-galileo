# Handoff: orquestador para documentar los cursos de Coursera

Este documento es el encargo completo para una sesión nueva que actuará como orquestador. No asume ningún contexto previo: todo lo que necesitas saber está aquí.

## 1. Objetivo

Documentar, curso por curso, el IBM Data Science Professional Certificate de Coursera, de forma que esa documentación sirva después como materia prima para construir un sistema de skills de análisis de datos.

El resultado no es un resumen de estudio. Es un catálogo de **métodos, criterios de decisión y verificaciones**, organizado por etapa del proceso de datos.

**Fuera de alcance:** escribir las skills, escribir código de análisis o construir el sistema. Eso se hará después, cuando el usuario termine el certificado. Aquí solo se documenta.

## 2. Contexto del usuario

- Médico con más de 15 años de experiencia clínica, en Medellín. Trabaja en analítica y herramientas digitales para una IPS.
- Está terminando el certificado. Cursos 1 a 6 completados; va en el curso 7, con el módulo 4 cubierto.
- Usa la IA para ejecutar; su foco es el criterio: cuándo usar cada método, en qué orden y cómo comprobar el resultado.
- Proyectos donde se aplicarán las skills: el Capstone del certificado, un modelo de precios de inmuebles de Medellín y, más adelante, analítica en salud.
- Idioma de toda la documentación: español, con el término técnico en inglés entre paréntesis la primera vez que aparece.

## 3. Cursos a documentar

Confirma con el usuario la lista vigente antes de empezar, porque IBM ha añadido cursos al programa.

| N.º | Curso | Prioridad | Motivo |
|---|---|---|---|
| 3 | Data Science Methodology | Alta | Da el esqueleto de etapas (CRISP-DM) |
| 6 | Databases and SQL for Data Science with Python | Media | Extracción y consulta de datos |
| 7 | Data Analysis with Python | Alta | Limpieza, transformación, exploración, evaluación de modelos |
| 8 | Data Visualization with Python | Media | Elección de gráficos |
| 9 | Machine Learning with Python | Alta | Modelado y validación |
| 10 | Applied Data Science Capstone | Alta | Proceso completo de principio a fin |
| 1, 2, 4, 5 | Introductorios, herramientas y Python básico | Baja | Solo lo que aporte criterio; no documentar sintaxis |

## 4. Fuentes y sus límites

- **No tienes acceso a Coursera.** No intentes iniciar sesión ni extraer contenido del sitio.
- La fuente es el material que el usuario deposite en `fuentes/<curso>/`: transcripciones, cuadernos de laboratorio, notas propias, capturas. Si esa carpeta no existe o está vacía para un módulo, pídeselo y continúa con los demás.
- El temario público de cada curso sirve para armar la estructura, no para rellenar contenido.
- **Derechos de autor:** redacta con palabras propias. No copies transcripciones ni enunciados completos.
- **Código de honor:** no documentes respuestas de cuestionarios ni soluciones de tareas calificadas. De los laboratorios se documenta el método y la decisión, no la solución para entregar.
- **No inventes.** Si un módulo no tiene material, márcalo como pendiente. Si añades algo de conocimiento general que el curso no dice, etiquétalo como tal (ver campo «Origen» en la ficha).
- No incluyas datos de pacientes ni de la IPS en ningún archivo, y no envíes datos personales del usuario a servicios externos.

## 5. Qué se documenta: la ficha de método

Una ficha por cada método o decisión relevante. Todas con los mismos campos, en este orden:

1. **Nombre** del método, en español y en inglés.
2. **Etapa** del proceso: comprensión del problema, comprensión de los datos, preparación, modelado, evaluación o comunicación.
3. **Problema que resuelve**, en una o dos frases.
4. **Cuándo usarlo y cuándo no.**
5. **Alternativas y criterio para elegir** entre ellas (por ejemplo, normalizar frente a estandarizar; imputar frente a eliminar).
6. **Orden y requisitos previos**: qué debe haberse hecho antes y qué no debe hacerse antes.
7. **Verificaciones**: qué comprobar después de aplicarlo, redactado de forma que un script pueda evaluarlo como «pasa» o «falla» (filas antes y después, nulos, rangos, totales).
8. **Errores silenciosos**: fallos que no producen mensaje de error pero dan un resultado falso.
9. **Cuándo detenerse y preguntar**: casos en que la decisión depende del contexto y no debe automatizarse.
10. **Ejemplo del curso**: dataset usado, qué se hizo y resultado esperado, si el material lo indica.
11. **Fuente**: curso, módulo y laboratorio.
12. **Origen**: «curso» o «añadido por conocimiento general».
13. **Skill candidata** a la que alimenta (ver sección 7).

Si un campo no se puede llenar con el material disponible, escribe «No consta en la fuente»; no lo dejes vacío ni lo rellenes por suposición.

## 6. Temas que no pueden faltar

Aunque el curso los trate de pasada, deben quedar documentados con ficha propia, porque son los fallos más costosos:

- Dividir en entrenamiento y prueba antes de escalar o imputar (fuga de información).
- Conjunto de prueba apartado al inicio y usado una sola vez.
- Validación cruzada para comparar alternativas.
- Riesgo de probar muchas combinaciones y quedarse con la mejor (sobreajuste por selección).
- Correlaciones encontradas buscando entre muchos pares de variables.
- Indicadores calculados con pocos casos.
- Duplicación de filas en uniones de tablas.

## 7. Skills candidatas

La documentación debe poder agruparse así. No las escribas; solo asigna cada ficha a una.

| Skill candidata | Curso principal |
|---|---|
| Extracción y consultas SQL | 6 |
| Perfilado del dataset | 7 |
| Limpieza y transformación | 7 |
| Análisis exploratorio y relaciones entre variables | 7 |
| Visualización | 8 |
| Modelado | 7 y 9 |
| Evaluación y validación de modelos | 7 y 9 |
| Proceso completo y entrega | 3 y 10 |

## 8. Estructura de archivos de salida

```
docs/cursos/<NN-nombre-del-curso>/modulo-<NN>.md   Fichas de cada módulo
docs/catalogo/metodos-por-etapa.md                 Índice de todas las fichas por etapa
docs/catalogo/decisiones.md                        Todas las reglas «usar X o Y»
docs/catalogo/verificaciones.md                    Todas las comprobaciones, por etapa
docs/catalogo/datasets.md                          Datasets de los cursos y resultados conocidos
docs/pendientes.md                                 Módulos sin material y preguntas abiertas
```

`datasets.md` importa especialmente: esos datasets serán los casos de prueba del sistema, porque su resultado correcto ya se conoce.

## 9. Cómo orquestar

1. **Piloto primero.** Documenta un solo módulo (recomendado: preparación de datos del curso 7) y enséñaselo al usuario antes de continuar. Ajusta la ficha con su respuesta.
2. **Un agente por curso**, y por módulo en los cursos 7 y 9. Lanza en paralelo solo los que tengan material disponible.
3. **Traspasos por archivo.** Cada agente lee de `fuentes/` y escribe su archivo de módulo. No decidas a partir del resumen que te devuelva: lee el archivo.
4. **Instrucciones completas a cada agente.** Dale la ficha de la sección 5, los límites de la sección 4 y la ruta exacta de entrada y salida. No sabe nada más que lo que le escribas.
5. **Comprobación por script, no por opinión.** Escribe un script que valide que cada ficha tiene los 13 campos, que «Etapa», «Origen» y «Skill candidata» usan valores permitidos y que cada ficha cita su fuente. Ejecútalo tras cada agente.
6. **Revisor independiente.** Un agente distinto recibe el material fuente y las fichas, sin la explicación del autor, y busca: afirmaciones que la fuente no respalda, criterios mal trasladados y métodos omitidos. Úsalo en los cursos de prioridad alta.
7. **Consolidación al final.** Los catálogos de `docs/catalogo/` se generan a partir de las fichas, no se redactan aparte, para que no se contradigan.
8. **Mantén el número de agentes bajo.** Menos de diez en total; los cursos de prioridad baja puede hacerlos un solo agente.

## 10. Criterio de terminado

- Cada módulo con material tiene su archivo y pasa el script de validación.
- Los temas de la sección 6 tienen ficha.
- Los cuatro catálogos están generados y coinciden con las fichas.
- `pendientes.md` lista cada módulo sin material y cada duda sin resolver.
- El informe final al usuario separa tres grupos: documentado y verificado, documentado sin revisar, y no documentado con su motivo.

## 11. Git

Trabaja en la rama que tenga asignada tu sesión, con commits por curso. No abras un pull request salvo que el usuario lo pida.

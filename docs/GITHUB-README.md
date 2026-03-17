# Galileo - Ecosistema de Agentes Genérico

> **Disectar cualquier tarea en partes lógicas, asignar agentes especializados, aprender de cada ejecución.**

## Visión

Galileo es un sistema general para resolver **cualquier tipo de tarea** usando:
- LLM económica y de alto rendimiento (MiniMax)
- Descomposición de tareas en componentes lógicos
- Agentes especializados por tipo de componente
- Memoria que aprende y refina habilidades
- Seguridad integrada

## Estado Actual

### Faceta 1: Data Science (CRISP-DM) ✅
- Agentes especializados por fase
- Sistema de memoria jerárquica
- Skills de Superpowers
- Security Agent

### Más facetas: En desarrollo...

## 📋 Tabla de Contenidos

1. [Qué es este proyecto](#qué-es-este-proyecto)
2. [Requisitos previos](#requisitos-previos)
3. [Instalación paso a paso](#instalación-paso-a-paso)
4. [Cómo usar los agentes](#cómo-usar-los-agentes)
5. [Estructura del proyecto](#estructura-del-proyecto)
6. [Configuración de MCPs](#configuración-de-mcps)
7. [Memoria de agentes](#memoria-de-agentes)
8. [Seguridad](#seguridad)
9. [Solución de problemas](#solución-de-problemas)
10. [FAQ](#faq)

---

## 🤔 Qué es este proyecto

Este es un **ecosistema de agentes especializados** para proyectos de Data Science y Machine Learning, basado en la metodología **CRISP-DM**.

### Qué hace cada agente:

| Agente | Qué hace |
|--------|----------|
| **Coordinator** | Coordina todo el proyecto |
| **Business Agent** | Entiende objetivos de negocio |
| **Data Explorer Agent** | Explora los datos disponibles |
| **Data Engineer Agent** | Prepara los datos para el modelo |
| **ML Engineer Agent** | Entrena el modelo de ML |
| **Evaluation Agent** | Evalúa el modelo contra objetivos |
| **MLOps Agent** | Despliega a producción |
| **Security Agent** | Audita la seguridad |

### Por qué usarlo:

- ✅ Metodología probada (CRISP-DM)
- ✅ Agentes especializados por fase
- ✅ Memoria que aprende de errores
- ✅ Seguridad integrada

---

## 📦 Requisitos previos

### Software necesario:

```
✓ Python 3.10+ 
✓ Git
✓ Node.js 18+ (para MCPs)
✓ OpenClaw instalado
```

### Verificar instalación:

```bash
# Ver Python
python --version
# Debe mostrar: Python 3.10.x o superior

# Ver Git
git --version
# Debe mostrar: git version x.x.x

# Ver Node.js
node --version
# Debe mostrar: v18.x.x o superior
```

---

## 🚀 Instalación paso a paso

### Paso 1: Clonar el repositorio

```bash
# En tu terminal, navega a donde quieres el proyecto
cd ~

# Clona el repositorio (reemplaza con tu URL)
git clone https://github.com/tu-usuario/crispdm-agents.git

# Entra al directorio
cd crispdm-agents
```

### Paso 2: Crear entorno virtual (RECOMENDADO)

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Linux/Mac)
source venv/bin/activate

# Activar (Windows)
venv\Scripts\activate

# Verificar que está activo
# Debería mostrar (venv) al inicio de la línea
```

### Paso 3: Instalar dependencias

```bash
# Instalar librerías de Python
pip install -r requirements.txt

# Instalar MCPs necesarios (opcional)
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-git
```

### Paso 4: Configurar OpenClaw

```bash
# Inicializar OpenClaw (si no está instalado)
npm install -g openclaw

# Configurar (responde las preguntas)
openclaw configure
```

### Paso 5: Configurar MCPs

Edita el archivo de configuración de OpenClaw:

```bash
# Encuentra tu archivo de configuración
# Usualmente está en ~/.openclaw/config.yaml

# Agrega los MCPs:
mcpServers:
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "./data"]
  memory:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-memory"]
  git:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-git"]
```

### Paso 6: Reiniciar OpenClaw

```bash
# Reinicia el gateway
openclaw gateway restart
```

### Paso 7: Verificar instalación

```bash
# Ver estado
openclaw status

# Debería mostrar que está corriendo correctamente
```

---

## 🤖 Cómo usar los agentes

### Iniciar un nuevo proyecto

```bash
# Desde OpenClaw o tu cliente
# Simplemente describe tu proyecto

"Quiero predecir churn de clientes para mi empresa de telecom"
```

El Coordinator recibirá tu solicitud y comenzará automáticamente con el Business Agent.

### Flujo de trabajo típico:

```
1. Usuario → describe problema
         ↓
2. Coordinator → analiza y planifica
         ↓
3. Business Agent → define objetivos
         ↓
4. Data Explorer Agent → explora datos
         ↓
5. Data Engineer Agent → prepara datos
         ↓
6. ML Engineer Agent → entrena modelo
         ↓
7. Evaluation Agent → valida resultados
         ↓
8. MLOps Agent → despliega a producción
```

### Comandos útiles:

| Comando | Qué hace |
|---------|----------|
| `/start <proyecto>` | Iniciar nuevo proyecto |
| `/status` | Ver estado actual |
| `/phase <n>` | Ir a fase específica |
| `/report` | Generar reporte de progreso |
| `/help` | Ver ayuda |

---

## 📂 Estructura del proyecto

```
crispdm-agents/
├── agents/                    # Definiciones de agentes
│   ├── coordinator/          # Orchestrator principal
│   └── phases/              # Agentes por fase
│       ├── business-agent/
│       ├── data-explorer-agent/
│       ├── data-engineer-agent/
│       ├── ml-engineer-agent/
│       ├── evaluation-agent/
│       ├── mlops-agent/
│       └── security-agent/
│
├── skills/                   # Skills de Superpowers
│   └── superpowers/
│       ├── brainstorming/
│       ├── writing-plans/
│       ├── test-driven-development/
│       └── systematic-debugging/
│
├── memory/                   # Memoria de los agentes
│   ├── global/              # Lecciones globales
│   ├── types/               # Lecciones por tipo de proyecto
│   └── projects/           # Lecciones por proyecto específico
│
├── mcps/                    # Evaluación de MCPs
├── docs/                    # Documentación
└── data/                    # Datos del proyecto (creas esta carpeta)
```

---

## 🔌 Configuración de MCPs

### Qué son los MCPs?

Los **Model Context Protocols** son extensiones que dan capacidades adicionales a los agentes.

### MCPs recomendados:

| MCP | Para qué sirve | Priority |
|-----|----------------|----------|
| **Filesystem** | Leer/escribir archivos | Alta |
| **Memory** | Memoria persistente | Alta |
| **Git** | Control de versiones | Alta |
| **SQLite** | Consultas SQL | Media |

### Cómo agregar un MCP:

1. Instalar el paquete:
```bash
npm install -y @modelcontextprotocol/server-nombre
```

2. Agregar a config:
```yaml
mcpServers:
  nombre:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-nombre"]
```

3. Reiniciar OpenClaw:
```bash
openclaw gateway restart
```

---

## 🧠 Memoria de agentes

### Cómo funciona la memoria:

Los agentes **aprenden** de sus errores y éxitos. Cada vez que completan una fase, guardan lo que:

- ✅ Funcionó bien → Lo usan en proyectos futuros
- ❌ Falló → Lo evitan en proyectos futuros

### Niveles de memoria:

| Nivel | Qué guarda | Ejemplo |
|-------|------------|---------|
| **Global** | Errores que aplican a todos | "No hacer data leakage" |
| **Tipo** | Errores específicos de clasificación/NLP/etc | "No usar accuracy con clases desbalanceadas" |
| **Proyecto** | Lecciones de este proyecto específico | "La columna X tenía 40% nulos" |

### Ver la memoria:

```bash
# Ver lecciones globales
cat memory/global/patterns/failures.md

# Ver lecciones de un tipo de proyecto
cat memory/types/classification/patterns/failures.md

# Ver lecciones de un proyecto
cat memory/projects/mi-proyecto/learnings.md
```

---

## 🔒 Seguridad

### El Security Agent hace:

1. **Auditar** el código regularmente
2. **Detectar** vulnerabilidades
3. **Proponer** mejoras
4. **Verificar** que las protecciones funcionen

### Checklist de seguridad:

- ✅ No exponer API keys en código
- ✅ Usar variables de entorno
- ✅ Validar inputs de usuarios
- ✅ No guardar datos sensibles en texto plano
- ✅ Mantener dependencias actualizadas

### Ejecutar auditoría:

```bash
# El Security Agent puede auditar el sistema
# Simplemente pregunta: "Ejecuta una auditoría de seguridad"
```

---

## 🔧 Solución de problemas

### Error: "Command not found"

```bash
# Asegúrate de tener el entorno virtual activado
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### Error: "Module not found"

```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: MCP no conecta

```bash
# Verificar que el paquete está instalado
npm list -g @modelcontextprotocol/server-nombre

# Reiniciar OpenClaw
openclaw gateway restart
```

### OpenClaw no inicia

```bash
# Ver logs
openclaw gateway status
openclaw gateway logs

# Reinstalar si es necesario
npm install -g openclaw
```

---

## ❓ FAQ

### Puedo agregar mis propios agentes?

**Sí!** Simplemente crea una carpeta en `agents/phases/` con un archivo `SYSTEM.md`.

### Puedo usar otros modelos de LLM?

**Sí!** Configura tu preference en `~/.openclaw/config.yaml`.

### Los agentes guardan memoria entre sesiones?

**Sí!** Usan el sistema de memoria descrito arriba. La memoria se guarda en `memory/`.

### Es seguro exponer esto a internet?

**DEPENDE.** Recomendamos:
- Usar autenticación
- No exponer credenciales
- Revisar el Security Agent regularmente
- Usar en red privada para proyectos sensibles

### Dónde pido ayuda?

1. Revisa esta documentación
2. Busca en los issues de GitHub
3. Pregunta en la comunidad OpenClaw

---

## 📞 Soporte

- **GitHub Issues**: Reportar bugs
- **Discussions**: Preguntas a la comunidad
- **Documentación**: En la carpeta `docs/`

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b mi-mejora`)
3. Haz tus cambios
4. Commit (`git commit -am 'Agregué algo'`)
5. Push (`git push origin mi-mejora`)
6. Abre un Pull Request

---

## 📜 Licencia

MIT License - Ver archivo LICENSE

---

*Última actualización: 2026-03-16*
*Versión: 1.0.0*

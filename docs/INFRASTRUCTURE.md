# Infraestructura de Galileo - Estado Actual

## Resumen Ejecutivo

```
GALILEO = Ecosistema de Agentes para Resolución de Tareas
LLM Principal: MiniMax M2.5 (económica, alto rendimiento)
```

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    GALILEO SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │  FACETA 1   │    │  FACETA 2   │    │  FACETA N   │    │
│  │ Data Science│    │Investigación│    │   (Future)  │    │
│  │  (CRISP-DM)│    │   (Planning)│    │             │    │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    │
│         │                   │                   │           │
│    ┌────┴────┐         ┌────┴────┐         ┌────┴────┐     │
│    │ Agentes │         │ Agentes │         │ Agentes │     │
│    │ Especial│         │ Especial│         │ Especial│     │
│    └─────────┘         └─────────┘         └─────────┘     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              SISTEMA DE MEMORIA                      │   │
│  │  Global → Tipo → Proyecto (3 niveles)               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              SECURITY AGENT                          │   │
│  │  Auditoría, protección, validación                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCPs CONFIGURADOS                        │
├─────────────────────────────────────────────────────────────┤
│  filesystem  │  memory  │  git  │  sqlite  │  fetch       │
│  (Archivos)  │  (Graph) │ (Git) │  (DB)    │  (Web)       │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes Actuales

### 1. Agentes (8 total)

| Agente | Rol | Estado |
|--------|-----|--------|
| **Coordinator** | Orchestrator general | ✅ Listo |
| **Business Agent** | Objetivos de negocio (Fase 1) | ✅ Listo |
| **Data Explorer Agent** | Exploración de datos (Fase 2) | ✅ Listo |
| **Data Engineer Agent** | Preparación de datos (Fase 3) | ✅ Listo |
| **ML Engineer Agent** | Modelado ML (Fase 4) | ✅ Listo |
| **Evaluation Agent** | Evaluación (Fase 5) | ✅ Listo |
| **MLOps Agent** | Deployment (Fase 6) | ✅ Listo |
| **Security Agent** | Auditoría y seguridad | ✅ Listo |

### 2. Skills (5 total)

| Skill | Propósito |
|-------|-----------|
| **brainstorming** | Diseño antes de implementar |
| **writing-plans** | Crear planes de implementación |
| **subagent-driven-development** | Ejecutar con subagentes |
| **test-driven-development** | Metodología TDD |
| **systematic-debugging** | Debugging estructurado |

### 3. MCPs (5 total)

| MCP | Herramientas | Estado |
|-----|--------------|--------|
| **filesystem** | 14 (read, write, search, etc.) | ✅ Configurado |
| **memory** | Knowledge graph | ✅ Configurado |
| **git** | Version control | ✅ Configurado |
| **sqlite** | Base de datos | ✅ Configurado |
| **fetch** | Web fetching | ✅ Configurado |

### 4. Memoria (3 niveles)

| Nivel | Descripción | Estado |
|-------|-------------|--------|
| **Global** | Errores/patrones universales | ✅ Estructura lista |
| **Tipo** | Por tipo de proyecto | ✅ Estructura lista |
| **Proyecto** | Por proyecto específico | ✅ Estructura lista |

---

## Estructura de Archivos

```
galileo/
├── GALILEO.md                    # Visión del ecosistema
├── agents/
│   ├── coordinator/
│   │   └── SYSTEM.md            # Coordinator general
│   └── phases/
│       ├── business-agent/
│       ├── data-explorer-agent/
│       ├── data-engineer-agent/
│       ├── ml-engineer-agent/
│       ├── evaluation-agent/
│       ├── mlops-agent/
│       └── security-agent/
│
├── skills/
│   └── superpowers/             # Skills de metodología
│       ├── brainstorming/
│       ├── writing-plans/
│       ├── subagent-driven-development/
│       ├── test-driven-development/
│       └── systematic-debugging/
│
├── memory/
│   ├── HIERARCHY.md            # Sistema de memoria
│   ├── SYSTEM.md
│   ├── global/                 # Lecciones globales
│   ├── types/                  # Lecciones por tipo
│   └── projects/              # Lecciones por proyecto
│
├── mcps/
│   ├── CONFIGURED.md           # MCPs activos
│   └── EVALUATION.md
│
├── repos/
│   └── EVALUATION.md           # Repos evaluados
│
├── config/
│   └── mcporter.json           # Configuración MCPs
│
├── data/                       # Datos de proyectos
└── docs/
    └── GITHUB-README.md        # Documentación
```

---

## Capacidades por MCP

### Filesystem MCP
- ✅ Leer archivos (texto, imagen, audio)
- ✅ Escribir archivos
- ✅ Editar archivos (línea por línea)
- ✅ Crear directorios
- ✅ Buscar archivos (patrones glob)
- ✅ Mover/renombrar
- ✅ Ver árbol de directorios
- ⚠️ **ACCESO TOTAL AL SISTEMA** (requiere seguridad)

### Memory MCP
- ✅ Crear entidades
- ✅ Crear relaciones
- ✅ Buscar entidades
- ✅ Agregar observaciones
- ✅ Persistencia en archivo local

### Git MCP
- ✅ Status, diff, log
- ✅ Buscar en código (grep)
- ✅ Branching (crear, cambiar, listar)
- ✅ Commits
- ⚠️ **Requiere validación** para operaciones destructivas

### SQLite MCP
- ✅ Listar tablas
- ✅ Ver schema
- ✅ Ejecutar SQL (SELECT, INSERT, UPDATE, DELETE)
- ⚠️ **Requiere validación** para DROP/ALTER

### Fetch MCP
- ✅ Obtener páginas web
- ✅ Limitar caracteres
- ✅ APIs REST
- ⚠️ **Requiere whitelist** de URLs permitidas

---

## LLM y Pricing

| Modelo | Contexto | Costo Input | Costo Output |
|--------|----------|-------------|--------------|
| **MiniMax M2.5** | 200k | $0.30/1M | $1.20/1M |

**Estrategia actual:**
- Solo MiniMax como modelo principal
- DeepSeek para tareas simples+pesadas (futuro)
- Escalado a servidor/VPS según demanda

---

## Puntos Críticos a Evaluar

### 1. 🔴 SEGURIDAD - Filesystem Acceso Total
El MCP de filesystem tiene acceso a TODO el PC. Esto es arriesgado.

**Problema:** Un actor malicioso podría:
- Leer archivos sensibles (keys, passwords)
- Borrar archivos del sistema
- Escribir malware

**Solución requerida:** Limitar directorios permitidos

### 2. 🟡 Memoria MCP - Persistencia
El knowledge graph se guarda en archivo local. Necesitamos:
- Backup automático
- Limpieza periódica
- maybe migrar a base de datos

### 3. 🟢 Git MCP - Seguro
Solo operaciones de lectura por defecto. Destructive ops requieren confirmación.

### 4. 🟢 SQLite MCP - Seguro
Solo acceso a archivo .db específico. No puede acceder a otras bases.

### 5. 🟡 Fetch MCP - Puede Mejorar
Por defecto puede acceder a cualquier URL. Necesitamos whitelist.

---

## Siguiente Paso

**Evaluación de seguridad** - Ver documento `security/INFRASTRUCTURE_SECURITY.md`

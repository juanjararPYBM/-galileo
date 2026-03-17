# 🏥 Galileo: From Physician to Architect

> *How a doctor built an AI agent ecosystem in one afternoon after two weeks of struggling*

---

## The Journey

### The Beginning: A Doctor Learning Data Science

I started the IBM Data Science Professional Certificate to transition from 13 years in medicine to Health Data Science.

Then came Module 3: apply CRISP-DM methodology to a real dataset.

### The Discovery: Vibe Coding

Instead of learning to code properly, I discovered **vibe coding** — asking AI to write code, then fixing its errors. Gemini was an "absolute madness, extremely complex and inefficient."

I tried Kimi, Kilo, the free version of MiniMax... until I found Claude. I completed the project, but made it **way more complex than necessary** — mixing Python with CSS, JS, and HTML5 instead of using simple visualization libraries.

### The Problem: Token Hell

The project grew too big for Colab. I moved to GitHub Pages to present it. Then reality hit:

> **Claude tokens were being consumed at an alarming rate.**

### The Search: DeepSeek & The Architecture

I started exploring solutions. The idea emerged:

- **Claude** = Brain (strategy, planning, expensive)
- **DeepSeek** = Muscle (execution, cheap)

I began designing **Galileo** — an ecosystem where Claude orchestrates and DeepSeek executes.

### The Crisis: Claude Ban Risk

Research revealed: using Claude API tokens in external tools carried a **ban risk**. My options:
1. Stay with Claude in OpenClaw (risky)
2. Move everything to Claude Code

### The Breakthrough: MiniMax M2.5

Researching with DeepSeek, I discovered:

> **MiniMax M2.5 rivals Claude in quality, DeepSeek in price.**

And it has a **Coding Plan** that integrates directly into OpenClaw via OAuth.

### The Day Everything Changed: March 16, 2026

After two weeks of struggling with:
- Skills that wouldn't load
- Corrupted JSON configs
- API keys that wouldn't work
- Error cascades

**One afternoon with MiniMax, I built what took weeks to design:**

```
GALILEO = 8 agents + 11 MCPs + security + memory + 2 facets
```

---

## What is Galileo?

**Galileo** is a generic task-solving agent ecosystem that:
1. Dissects any task into logical parts
2. Assigns specialized agents to each part
3. Learns from every execution
4. Maintains security at every level

### Facet 1: Data Science (CRISP-DM) ✅

7 specialized agents:
- Business Agent
- Data Explorer Agent
- Data Engineer Agent
- ML Engineer Agent
- Evaluation Agent
- MLOps Agent
- Security Agent

### Facet 2: Research ✅

2 specialized agents:
- Research Agent
- Data Collector Agent

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    COORDINATOR                       │
│                  (Galileo Brain)                     │
└─────────────────────┬───────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Faceta 1 │   │ Faceta 2 │   │  More    │
│   DS     │   │Research  │   │Facets    │
│(CRISP-DM)│   │          │   │(Future)  │
└──────────┘   └──────────┘   └──────────┘
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| LLM | MiniMax M2.5 |
| Orchestrator | OpenClaw |
| Memory | 3-level hierarchical |
| Security | Rate limiting, whitelist, validation |
| MCPs | 11 configured |

### MCPs Configured

```
✅ filesystem     → File management
✅ memory        → Knowledge graph
✅ git           → Version control
✅ sqlite        → Database
✅ fetch         → Web pages
✅ brave-search  → Web search
✅ exa-search    → Semantic search
✅ firecrawl     → Advanced scraping
✅ pdf-parser    → Academic papers
✅ playwright    → Web automation
✅ notion       → Knowledge base
```

---

## Security Features

- **Whitelist** directories and domains
- **Rate limiting** (global + per MCP)
- **Prompt injection** detection (27 patterns)
- **Command blocking** for git, SQL
- **Complete logging** of all operations
- **Security Agent** for continuous auditing

---

## Why This Matters

> *"Instead of spending years learning Python and R to do this, with AI help I structured it in one afternoon after 2 weeks of going from AI to AI."*

I'm a physician who found in AI not just a tool, but a **new way to solve problems**. Galileo isn't just a project — it's proof that the barrier to entry for complex AI systems is lower than ever.

---

## Connect

- **GitHub**: [juanjararPYBM](https://github.com/juanjararPYBM)
- **LinkedIn**: [Juan Pablo Jaramillo](https://www.linkedin.com/in/juanjararhad/)
- **Location**: Medellín, Colombia

---

## The Philosophy

```
Médico (diagnosis of complex systems)
    ↓
Aprendiz de ciencia de datos (seeking credentials)
    ↓
Explorador de IA (vibe coding & agents)
    ↓
Arquitecto de sistemas cognitivos (designing ecosystems)
```

---

## What's Next?

- [ ] Add more facets (Development, Automation)
- [ ] Scale to server
- [ ] Add more models
- [ ] Community contributions

---

*Galileo — a telescope to observe and understand the data universe*

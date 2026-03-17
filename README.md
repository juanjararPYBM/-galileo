# 🔭 Galileo

## The AI Agent Ecosystem That Took One Afternoon to Build (After Two Weeks of Struggling)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/Status-Active-green.svg)](https://github.com/juanjararPYBM/galileo)

> From physician to architect — how I built a complete AI agent ecosystem in one afternoon after discovering MiniMax M2.5

### The Short Version

**Two weeks** of struggling with Claude tokens, OpenClaw configs, and API keys.

**One afternoon** with MiniMax M2.5.

**The result**: An entire agent ecosystem with 8 agents, 11 MCPs, security, memory, and 2 complete facets.

---

## 🚀 Quick Start

```bash
# Clone the project
git clone https://github.com/juanjararPYBM/galileo.git
cd galileo

# (Configure your MiniMax API key)
# (Run with OpenClaw)

# Start exploring!
```

---

## 📖 Read the Full Story

The complete journey from physician to AI architect:

📖 **[THE_HERO_STORY.md](./THE_HERO_STORY.md)**

---

## 🏗️ Architecture

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

## ✨ Features

### Core Capabilities
- **Multi-facet system**: Data Science + Research + more coming
- **Specialized agents**: Each task gets the right agent
- **Hierarchical memory**: Learn from every execution
- **Complete security**: Rate limiting, validation, logging

### Data Science Facet (CRISP-DM)
- ✅ Business Agent — Business objectives
- ✅ Data Explorer Agent — Data exploration
- ✅ Data Engineer Agent — Data preparation
- ✅ ML Engineer Agent — Model training
- ✅ Evaluation Agent — Model evaluation
- ✅ MLOps Agent — Deployment

### Research Facet
- ✅ Research Agent — Analysis and synthesis
- ✅ Data Collector Agent — Secure data extraction

### MCPs Configured (11)
| MCP | Purpose |
|-----|---------|
| filesystem | File management |
| memory | Knowledge graph |
| git | Version control |
| sqlite | Database |
| fetch | Web pages |
| brave-search | Web search |
| exa-search | Semantic search |
| firecrawl | Advanced scraping |
| pdf-parser | Academic papers |
| playwright | Web automation |
| notion | Knowledge base |

---

## 🔒 Security

- 27 prompt injection patterns detected
- Whitelist directories (6) and domains (16)
- Rate limiting (global + per MCP)
- Complete operation logging
- Security Agent for continuous auditing

**Score: 86%** — [See full audit](./security/AUDIT.md)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [THE_HERO_STORY.md](./THE_HERO_STORY.md) | The complete journey |
| [GALILEO.md](./GALILEO.md) | Architecture overview |
| [security/AUDIT.md](./security/AUDIT.md) | Security audit |
| [docs/](./docs/) | Technical documentation |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | MiniMax M2.5 |
| Orchestrator | OpenClaw |
| Memory | 3-level hierarchical |
| Security | Custom validators |

---

## 👤 About the Author

**Juan Pablo Jaramillo** — *Physician → Health Data Science*

- 13+ years in medicine (Oncology & Palliative Care)
- Transitioning to Health Data Science
- IBM Data Science Certificate
- Building the future of AI-assisted healthcare

📍 Medellín, Colombia

🔗 [GitHub](https://github.com/juanjararPYBM) | [LinkedIn](https://www.linkedin.com/in/juanjararhad/)

---

## 🤝 Contributing

This is a personal project but feedback is welcome! 

---

## 📝 License

MIT — See [LICENSE](./LICENSE)

---

*Built with passion for what AI can achieve. The barrier to entry is lower than ever.*

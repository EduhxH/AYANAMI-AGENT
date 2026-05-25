# AYANAMI-AGENT

![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Release](https://img.shields.io/github/v/release/EduhxH/AYANAMI-AGENT?style=for-the-badge&color=7c3aed)

A multi-agent AI system for automating developer workflows — inspired by Rei Ayanami from Neon Genesis Evangelion.

🇺🇸 This project is documented and implemented entirely in American English.

-----

## About

AYANAMI-AGENT is a production-grade AI agent orchestration system built with FastAPI and Next.js. It routes natural language queries to specialized agents — GitHub, Email, and Anime — through a central Orchestrator that resolves inter-agent dependencies before dispatching.

Queries like *“analyze my GitHub and send a summary to my email”* trigger a dependency-aware pipeline: GitHubAgent runs first, fetches real repository metadata (language, description, topics, stars), and injects a structured context into EmailAgent before it composes and sends a narrative analysis — not a raw list.

This project builds on the foundations of [MCP-SERVER-PRO](https://github.com/EduhxH/MCP-SERVER-PRO), [IA-agent-with-tools](https://github.com/EduhxH/IA-agent-with-tools---), and [AGENTE-IA](https://github.com/EduhxH/AGENTE-IA), and represents the most architecturally complete iteration to date.

-----

## Agents

|Agent            |Description                                                                                                                                                                       |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|🐙 **GitHubAgent**|Analyzes repositories with full metadata (language, description, topics, stars), creates repos with LLM-generated READMEs, resolves SHA conflicts on the GitHub Contents API      |
|📧 **EmailAgent** |Sends and drafts emails via Gmail OAuth; classifies intent using Groq with forced `json_object` response format; composes narrative GitHub analysis emails from real repo metadata|
|🌸 **AnimeAgent** |Recommends anime based on the user’s technical profile — easter egg feature                                                                                                       |

-----

## Architecture

```
User Query
    │
    ▼
Orchestrator — detects agents required
    │
    ▼
Dispatcher — resolves dependencies
    │
    ├── GitHubAgent (runs first if Email depends on it)
    │       └── structured metadata injected into EmailAgent context
    │               (language, description, topics, stars per repo)
    │
    └── Remaining agents (parallel)
```

**Key design decisions:**

- When a query requires both GitHub and Email, the Dispatcher runs GitHubAgent first and awaits its result before dispatching EmailAgent — preventing data dependency failures from parallel execution.
- GitHubAgent passes structured per-repo metadata (not just names) so the LLM produces accurate, specialization-aware analysis.
- `AgentResult` carries `message` and `errors` fields for full traceback visibility on failure.
- EmailAgent intent classification uses `response_format={"type": "json_object"}` at the Groq API level, eliminating silent classifier failures from empty or malformed LLM responses.
- Rate limiting applied to the `/query/` endpoint to prevent abuse in production.

-----

## Tech Stack

|Layer     |Technology                                    |
|----------|----------------------------------------------|
|Backend   |Python 3.11+, FastAPI, Uvicorn, httpx, asyncio|
|LLM       |Groq (`llama-3.3-70b-versatile`)              |
|Database  |MongoDB Atlas                                 |
|Auth      |GitHub OAuth, Google OAuth                    |
|Email     |Gmail API                                     |
|Frontend  |Next.js, React, TypeScript, TailwindCSS       |
|Deployment|Vercel (frontend), Railway (backend)          |
|Testing   |pytest, pytest-asyncio, unittest.mock         |

-----

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm
- MongoDB instance (local or Atlas)

### Backend

```bash
git clone https://github.com/EduhxH/AYANAMI-AGENT.git
cd AYANAMI-AGENT/backend
pip install -r requirements.txt
cp .env.example .env  # fill in your credentials
uvicorn dev_agent.api.app:app --reload
```

### Frontend

```bash
cd ../frontend
pnpm install
cp .env.example .env.local  # fill in your credentials
pnpm dev
```

### Tests

```bash
# Unit tests
python quick_validate.py

# Integration tests
pytest backend/tests/test_integration.py -v
```

-----

## Configuration

Key environment variables (see `.env.example` for the full list):

```env
# Groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile

# MongoDB
MONGODB_URL=mongodb+srv://...

# GitHub OAuth
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

-----

## Project Structure

```
AYANAMI-AGENT/
├── backend/
│   ├── src/dev_agent/
│   │   ├── agents/          # GitHubAgent, EmailAgent, AnimeAgent
│   │   ├── api/             # FastAPI routes
│   │   ├── core/            # AgentResult, models
│   │   ├── database/        # MongoDB
│   │   ├── orchestrator/    # Dispatcher, dependency resolution
│   │   └── tools/           # GitHub writer/reader, Gmail client
│   └── tests/               # Integration tests (pytest)
├── frontend/
│   ├── app/                 # Next.js pages
│   ├── components/          # React components
│   └── public/              # Static assets, custom cursors
├── .env.example
└── vercel.json
```

-----

## What I Learned

- **Dependency-aware orchestration** — parallelism breaks when agents depend on each other’s output; sequential dispatch with context injection solves it cleanly
- **GitHub Contents API** — updating an existing file requires a SHA lookup before the PUT; skipping it causes HTTP 422
- **LLM classifier reliability** — `response_format={"type": "json_object"}` at the API level is more reliable than prompt-only JSON enforcement
- **Async error handling** — wrapping agent `run()` in try/except with full traceback in `AgentResult` makes production debugging tractable
- **Context quality matters** — passing structured metadata (language, description, topics) instead of just repo names produces dramatically better LLM output

-----

## Live Demo

[ayanami-agent.vercel.app](https://ayanami-agent.vercel.app)

-----

## Contributing

Issues and pull requests are welcome.

-----

## License

MIT — see [LICENSE](./LICENSE)

-----

Made with 💜 by [EduhxH](https://github.com/EduhxH)
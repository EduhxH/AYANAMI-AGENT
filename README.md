<div align="center">

# AYANAMI-AGENT

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)

*A modular AI agent system designed to streamline development workflows — combining intelligent automation, LLM orchestration, and a clean full-stack interface.*

[![Live Demo](https://img.shields.io/badge/Live%20Demo-ayanami--agent.vercel.app-6366f1?style=for-the-badge&logo=vercel&logoColor=white)](https://ayanami-agent.vercel.app)

🇺🇸 This project is documented and implemented entirely in American English.

</div>

-----

> [!WARNING]
> **Account registration is currently disabled.**
> The email verification flow (powered by [Resend](https://resend.com)) was one of the last features added to this project and has not yet been activated. As a result, the sign-up functionality is unavailable at this time.

-----

> [!NOTE]
> **Want to try the live demo?** Since registration is disabled, use the test account below to log in at [ayanami-agent.vercel.app](https://ayanami-agent.vercel.app).
> 
> ```
> Email:    demoteste@teste.com
> Password: pass123
> ```
> 
> ⚠️ This is a shared account — please don’t change the password or delete any data.

-----

## Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
- [Configuration](#️-configuration)
- [Project Structure](#-project-structure)
- [Architecture Overview](#️-architecture-overview)
- [Known Limitations](#️-known-limitations)
- [What I Learned](#-what-i-learned)

-----

## 🧩 About

AYANAMI-AGENT is a modular AI agent system built to assist developers with intelligent, context-aware automation. It represents a significant leap forward from earlier projects — including [AGENTE-IA](https://github.com/EduhxH/AGENTE-IA), [IA-agent-with-tools](https://github.com/EduhxH/IA-agent-with-tools---), and [MCP-SERVER-PRO](https://github.com/EduhxH/MCP-SERVER-PRO) — and marks a natural evolution in architecture, tooling, and scope.

The system combines a high-performance FastAPI backend with a Next.js frontend, orchestrating specialized agents for code analysis, email automation, and developer productivity — all powered by Groq’s fast LLM inference.

Queries like *“analyze my GitHub and send a summary to my email”* trigger a dependency-aware pipeline: GitHubAgent runs first, fetches real repository metadata (language, description, topics, stars), and injects a structured context into EmailAgent before it composes and sends a narrative analysis — not a raw list.

-----

## ✨ Features

|Agent / Component         |Description                                                                                                                                                                        |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|🐙 **GitHub Agent**        |Analyzes repositories with full metadata (language, description, topics, stars), creates repos with LLM-generated READMEs, and resolves SHA conflicts on the GitHub Contents API.  |
|📧 **Email Agent**         |Sends and drafts emails via Gmail OAuth. Classifies intent using Groq with forced `json_object` response format. Composes narrative GitHub analysis emails from real repo metadata.|
|📁 **File Analysis**       |Accepts file uploads — source code, documents, and `.zip` archives — and processes their full contents for contextual analysis.                                                    |
|🌸 **Anime Agent**         |A hidden feature that generates personalized recommendations based on the user’s technical profile.                                                                                |
|⚡ **FastAPI Backend**     |High-performance, async-ready API powering all agent orchestration and routing logic.                                                                                              |
|⚛️ **Next.js Frontend**    |Responsive, minimalist UI built with Next.js and React for a seamless user experience.                                                                                             |
|🍃 **MongoDB Integration** |Flexible, scalable data storage for agent state, user profiles, and session data.                                                                                                  |
|🧠 **Groq LLM Integration**|Fast language model inference via Groq, used across all agents for reasoning and generation.                                                                                       |

-----

## 🛠️ Tech Stack

|Technology  |Role                            |
|------------|--------------------------------|
|Python 3.11+|Core backend language           |
|FastAPI     |Backend API framework           |
|MongoDB     |NoSQL database                  |
|Groq        |LLM provider                    |
|Next.js     |React framework for the frontend|
|React       |UI library                      |
|TypeScript  |Type-safe JavaScript            |
|TailwindCSS |Utility-first styling           |
|pytest      |Integration and unit testing    |

-----

## 📦 Prerequisites

- Python 3.11+
- Node.js 18+
- `pnpm` (recommended for frontend)
- MongoDB instance (local or Atlas)

-----

## 🚀 Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/EduhxH/AYANAMI-AGENT.git
cd AYANAMI-AGENT
```

**2. Backend setup**

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in your credentials
uvicorn dev_agent.api.app:app --reload
```

**3. Frontend setup**

```bash
cd ../frontend
pnpm install
cp .env.example .env.local   # fill in your credentials
pnpm dev
```

**4. Run tests**

```bash
# Unit tests
python quick_validate.py

# Integration tests
pytest backend/tests/test_integration.py -v
```

-----

## ⚙️ Configuration

Both `backend/` and `frontend/` include `.env.example` files. Copy and populate them before running the project.

```env
# App
SECRET_KEY=your_secret_key
ENVIRONMENT=development

# MongoDB Atlas
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/devagent

# Groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_SEARCH_MODEL=groq/compound-mini
GROQ_SEARCH_MODEL_LIVE=groq/compound
# GROQ_SEARCH_COUNTRY=portugal

# Resend (email — not yet activated)
RESEND_API_KEY=re_...
FROM_EMAIL=noreply@yourdomain.com

# GitHub OAuth
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GITHUB_REDIRECT_URI=http://localhost:8000/auth/callback/github

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/google

# Frontend
FRONTEND_URL=http://localhost:3000

# Optional fallback (only if Compound fails)
# TAVILY_API_KEY=tvly-...
```

-----

## 📁 Project Structure

```
AYANAMI-AGENT/
├── backend/
│   ├── src/
│   │   └── dev_agent/
│   │       ├── agents/         # Modular AI agents (GitHub, Email, Anime)
│   │       ├── api/            # FastAPI app and route definitions
│   │       ├── core/           # Core utilities and shared models
│   │       ├── database/       # MongoDB connection and schemas
│   │       ├── orchestrator/   # Agent dispatching and planning logic
│   │       └── tools/          # External tool integrations
│   ├── tests/                  # Integration tests (pytest)
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── app/                    # Next.js pages
│   ├── components/             # Reusable React components
│   ├── public/                 # Static assets (images, cursors)
│   ├── next.config.mjs
│   └── package.json
├── .env.example
├── .gitignore
└── vercel.json
```

-----

## 🏗️ Architecture Overview

Requests from the frontend hit the FastAPI backend, which passes them to the **Orchestrator**. The Orchestrator analyzes the intent and routes the request to the appropriate agent. Each agent has access to its own set of tools and returns a structured response back through the API.

When a query requires both GitHub and Email, the Dispatcher runs GitHubAgent first, injects its structured metadata output (language, description, topics, stars per repo) into EmailAgent’s context, and only then dispatches the email flow — preventing data dependency failures from parallel execution.

```
Frontend (Next.js)
      │
      ▼
FastAPI Backend
      │
      ▼
  Orchestrator  ──── routes to ────►  GitHub Agent  (GitHub API)
                                  ►  Email Agent   (Google API)
                                  ►  Anime Agent   (Groq LLM)
      │
      ▼
  Dispatcher  ──── dependency resolution ────►  GitHub → Email context injection
      │
      ▼
  MongoDB  (session data, agent state)
```

All agents share the same Groq LLM connection for reasoning and generation, keeping inference fast and centralized.

-----

## ⚠️ Known Limitations

- **Account registration is disabled** — Resend email verification has not been activated yet (see warning above).
- **UI bugs are expected** — this project is in active development. You **will** encounter layout inconsistencies and broken states, particularly on different screen sizes. If you find one, opening an issue is appreciated.
- **No multi-tenancy** — the current data model is not designed for large-scale multi-user isolation.
- **Groq rate limits** — free-tier Groq accounts have request limits that may affect response speed under heavy use.
- **Email Agent scope** — currently limited to Google accounts authenticated via OAuth; other providers are not supported.

-----

## 🧠 What I Learned

- **Dependency-aware orchestration** — parallelism breaks when agents depend on each other’s output; sequential dispatch with context injection solves it cleanly.
- **GitHub Contents API** — updating an existing file requires a SHA lookup before the PUT; skipping it causes HTTP 422.
- **LLM classifier reliability** — `response_format={"type": "json_object"}` at the API level is more reliable than prompt-only JSON enforcement.
- **Async error handling** — wrapping agent `run()` in try/except with full traceback in `AgentResult` makes production debugging tractable.
- **Context quality matters** — passing structured metadata (language, description, topics) instead of just repo names produces dramatically better LLM output.
- **Modular agent architecture** — designing extensible agent pipelines that can be expanded without breaking existing flows.
- **Full-stack integration** — connecting a FastAPI backend to a Next.js frontend with clean API boundaries and proper state handling.
- **External API integration** — building robust connectors for GitHub and Google services to extend agent capabilities.

-----

## 🤝 Contributing

Contributions are welcome. If you find a bug or want to propose a feature, open an issue first so we can discuss it before any code is written. When submitting a pull request, keep the scope focused — one fix or feature per PR.

-----

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

-----

<div align="center">
  Made with 💜 by <a href="https://github.com/EduhxH">EduhxH</a>
</div>
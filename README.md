# AYANAMI-AGENT

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)

> An intelligent AI agent system inspired by Evangelion — modular agents for GitHub analysis, email automation, and file-level code review, built on FastAPI + Next.js.

🇺🇸 This project is documented and implemented entirely in American English.

**[About](#-about) · [Try It](#-try-it) · [What's New](#-whats-new) · [Features](#-features) · [Tech Stack](#️-tech-stack) · [Getting Started](#-getting-started) · [Configuration](#️-configuration) · [Project Structure](#-project-structure)**

---

## 🧩 About

AYANAMI-AGENT is a modular AI agent system designed to streamline development workflows. It builds on the foundations of [MCP-SERVER-PRO](https://github.com/EduhxH/MCP-SERVER-PRO), [IA-agent-with-tools---](https://github.com/EduhxH/IA-agent-with-tools---), and [AGENTE-IA](https://github.com/EduhxH/AGENTE-IA) — each iteration pushing further into practical agent orchestration.

Inspired by Rei Ayanami from Neon Genesis Evangelion, the project combines a high-performance FastAPI backend with a minimalist Next.js interface. Agents handle real tasks: reading your repositories, managing emails, analyzing uploaded code, and recommending anime based on your technical profile.

---

## 🆕 What's New

### v2.0 — File Analysis & Integration Stability

**File Upload & Analysis System**
The most significant capability addition. The agent can now receive files directly — source code, documents, and compressed archives — and process their contents as part of any task. Uploading a `.zip` of a project allows the agent to analyze the full codebase in a single interaction, without manual file-by-file sharing.

**GitHub & Google Integration Fixes**
Resolved critical authentication failures in both the GitHub and Google connectors. OAuth flows and API communication are now stable, ensuring repository reads and email operations work reliably end-to-end.

**UI & Repository Cleanup**
Interface refinements to tighten alignment with the Evangelion aesthetic. Repository structure cleaned up — removed artifacts like `.claude/` — making the codebase ready for external contributors.

---

## ✨ Features

| Agent / Component | Description |
|---|---|
| 🐙 **GitHub Agent** | Authenticates via OAuth, reads repositories, identifies issues, and suggests code quality improvements. |
| 📧 **Email Agent** | Connects to Google to automate email responses and organize communication. |
| 📁 **File Analysis** | Accepts file uploads (source code, documents, `.zip` archives) and processes their contents for contextual analysis. |
| 🌸 **Anime Agent** | Recommends anime based on your technical stack and developer profile — with genuine cultural and technical justifications. |
| 🧠 **Agent Orchestrator** | Dispatches tasks across agents dynamically, with context-aware planning per request. |

---

## 🛠️ Tech Stack

| Layer | Technology | Role |
|---|---|---|
| **Backend** | Python 3.11+ | Core runtime |
| | FastAPI | REST API + agent routing |
| | Groq (`llama-3.3-70b`, `compound`) | LLM inference |
| | MongoDB Atlas | Persistent storage |
| **Frontend** | Next.js + React | UI framework |
| | TypeScript | Type safety |
| | TailwindCSS | Styling |
| **Integrations** | GitHub OAuth + API | Repository access |
| | Google OAuth + Gmail | Email automation |
| | Resend | Transactional email |

---

## 📦 Prerequisites

- Python 3.11+
- Node.js 18+
- `pnpm` (recommended)
- MongoDB instance (local or Atlas)
- Groq API key

---

## 🚀 Getting Started

**1. Clone**
```bash
git clone https://github.com/EduhxH/AYANAMI-AGENT.git
cd AYANAMI-AGENT
```

**2. Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env       # fill in your credentials
uvicorn dev_agent.api.app:app --reload
```

**3. Frontend**
```bash
cd ../frontend
pnpm install
cp .env.example .env.local  # fill in your credentials
pnpm dev
```

---

## ⚙️ Configuration

Copy `.env.example` → `.env` (backend) and `.env.example` → `.env.local` (frontend).

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

# Resend
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
```

---

## 📁 Project Structure

```
AYANAMI-AGENT/
├── backend/
│   ├── src/
│   │   └── dev_agent/
│   │       ├── agents/          # GitHub, Email, Anime, File agents
│   │       ├── api/             # FastAPI routes and app entrypoint
│   │       ├── core/            # Config, auth, utilities
│   │       ├── database/        # MongoDB models and connection
│   │       ├── orchestrator/    # Agent dispatching and task planning
│   │       └── tools/           # External integrations (GitHub, Google, Resend)
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── app/                     # Next.js pages
│   ├── components/              # Reusable React components
│   └── public/                  # Static assets and cursors
├── .env.example
├── vercel.json
└── README.md
```

---

## 🧠 What I Learned

**Modular Agent Design** — Building agents as independent, composable units that can be orchestrated without tight coupling between them.

**File Processing Pipeline** — Handling multipart uploads, decompressing archives server-side, and feeding extracted content into LLM context without hitting token limits.

**OAuth Reliability** — Debugging token refresh flows and callback edge cases across GitHub and Google providers.

**Full-stack LLM Integration** — Managing context windows, streaming responses, and maintaining state across a FastAPI backend and Next.js frontend.

---

## 🤝 Contributing

Issues and pull requests are welcome. Please open an issue first for significant changes.

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">Made with 💜 by <a href="https://github.com/EduhxH">EduhxH</a></p>

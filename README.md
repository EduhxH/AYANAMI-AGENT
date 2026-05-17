# AYANAMI-AGENT

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)

> An intelligent AI agent system inspired by Neon Genesis Evangelion — designed to streamline development workflows through modular agents and a sleek, minimalist interface.

🇺🇸 This project is documented and implemented entirely in American English.

-----

> [!WARNING]
> **Account registration is currently disabled.**
> The email verification flow (powered by [Resend](https://resend.com)) was one of the last features added to this project and has not yet been activated. As a result, the sign-up functionality is unavailable at this time.

-----

## Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
- [Configuration](#️-configuration)
- [Project Structure](#-project-structure)
- [What I Learned](#-what-i-learned)

-----

## 🧩 About

AYANAMI-AGENT is a modular AI agent system built to assist developers with intelligent, context-aware automation. It represents a significant leap forward from earlier projects — including [AGENTE-IA](https://github.com/EduhxH/AGENTE-IA), [IA-agent-with-tools](https://github.com/EduhxH/IA-agent-with-tools---), and [MCP-SERVER-PRO](https://github.com/EduhxH/MCP-SERVER-PRO) — and marks a natural evolution in architecture, tooling, and scope.

Inspired by Rei Ayanami from *Neon Genesis Evangelion*, the project combines a high-performance FastAPI backend with a Next.js frontend, orchestrating specialized agents for code analysis, email automation, and even anime recommendations based on a developer’s technical profile.

-----

## ✨ Features

|Agent / Component         |Description                                                                                                                    |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------|
|🐙 **GitHub Agent**        |Analyzes repositories, identifies code quality issues, and suggests targeted improvements.                                     |
|📧 **Email Agent**         |Automates email interactions and helps organize developer communication workflows.                                             |
|🌸 **Anime Agent**         |An Easter egg feature that recommends anime based on the user’s technical profile — with cultural and technical justifications.|
|⚡ **FastAPI Backend**     |High-performance, async-ready API powering all agent orchestration and routing logic.                                          |
|⚛️ **Next.js Frontend**    |Responsive, minimalist UI built with Next.js and React for a seamless user experience.                                         |
|🍃 **MongoDB Integration** |Flexible, scalable data storage for agent state, user profiles, and session data.                                              |
|🧠 **Groq LLM Integration**|Fast language model inference via Groq, used across all agents for reasoning and generation.                                   |

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

## 🧠 What I Learned

- **Modular agent architecture** — designing extensible agent pipelines that can be expanded without breaking existing flows.
- **Full-stack integration** — connecting a FastAPI backend to a Next.js frontend with clean API boundaries and proper state handling.
- **LLM orchestration** — using Groq to coordinate fast inference across multiple specialized agents.
- **External API integration** — building robust connectors for GitHub and Google services to extend agent capabilities.
- **Thematic design** — embedding a consistent visual identity (Evangelion / Rei Ayanami aesthetic) across both the UI and the project’s overall narrative.

-----

## 🤝 Contributing

Contributions are welcome. Feel free to open issues or submit pull requests.

-----

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

-----

<div align="center">
  Made with 💜 by <a href="https://github.com/EduhxH">EduhxH</a>
</div>
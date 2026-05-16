# AYANAMI-AGENT

![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white) ![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black) ![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

## 🚀 AYANAMI-AGENT

An intelligent AI agent system inspired by Evangelion, designed to streamline development workflows and provide intelligent assistance through modular agents and a sleek interface.

🇺🇸 This project is documented and implemented entirely in American English.

About • Features • Tech Stack • Getting Started • Configuration • Project Structure

### 🧩 About the Project

AYANAMI-AGENT is a sophisticated AI agent system designed to streamline development workflows and provide intelligent assistance. Inspired by the iconic character Rei Ayanami from Neon Genesis Evangelion, this project combines cutting-edge AI capabilities with a sleek, minimalist interface to create a powerful and intuitive tool for developers.

It features a modular backend built with FastAPI and Python, integrating various specialized agents like the GitHub Agent for code analysis, an Email Agent for communication automation, and a unique Anime Agent for personalized recommendations. The frontend, crafted with Next.js and React, offers an intuitive user experience with a minimalist design and themed cursors, ensuring seamless interaction and a consistent aesthetic.

### ✨ Features

| Icon | Agent/Component | Description |
| :--- | :-------------- | :---------- |
| 🐙 | **GitHub Agent** | Analyzes repositories, identifies issues, and provides suggestions for code quality and improvements. |
| 📧 | **Email Agent** | Manages email interactions, automates responses, and helps organize communication. |
| 🌸 | **Anime Agent** | A unique Easter egg feature that recommends anime based on a developer's technical profile, offering technical and cultural justifications. |
| ⚡ | **FastAPI Backend** | High-performance API built with FastAPI for robust and scalable agent orchestration. |
| ⚛️ | **Next.js Frontend** | Intuitive and responsive web interface built with Next.js and React for seamless user interaction. |
| 🍃 | **MongoDB Integration** | Utilizes MongoDB for flexible and scalable data storage for agent data and user profiles. |
| 🧠 | **Groq LLM Integration** | Leverages Groq for fast and efficient language model interactions across all agents. |

### 🛠️ Tech Stack

| Technology | Role |
| :--------- | :--- |
| Python 3.11+ | Core Programming Language for Backend |
| FastAPI | Web Framework for Backend API |
| MongoDB | NoSQL Database for Data Storage |
| Groq | LLM Provider for Agent Intelligence |
| Next.js | React Framework for Frontend |
| React | JavaScript Library for Frontend UI |
| TypeScript | Superset of JavaScript for Type Safety |
| TailwindCSS | Utility-First CSS Framework for Styling |

### 📦 Prerequisites

Before getting started, make sure you have the following installed:

-   Python 3.11+
-   Node.js 18+
-   pnpm (recommended package manager for frontend)
-   MongoDB instance (local or cloud-hosted)

### 🚀 Getting Started

To get AYANAMI-AGENT up and running locally, follow these steps:

1.  **Clone the repository**

    ```bash
    git clone https://github.com/EduhxH/AYANAMI-AGENT.git
    cd AYANAMI-AGENT
    ```

2.  **Backend Setup**

    ```bash
    cd backend
    pip install -r requirements.txt
    # Create a .env file based on .env.example and fill in your credentials
    # cp .env.example .env
    uvicorn dev_agent.api.app:app --reload
    ```

3.  **Frontend Setup**

    ```bash
    cd ../frontend
    pnpm install
    # Create a .env.local file based on .env.example and fill in your credentials
    # cp .env.example .env.local
    pnpm dev
    ```

### ⚙️ Configuration

Both the `backend` and `frontend` directories contain `.env.example` files. Copy these to `.env` (for backend) and `.env.local` (for frontend) respectively, and populate them with your API keys and other necessary configurations.

Here are the key environment variables:

```ini
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

# Resend (email)
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

### 📁 Project Structure

```
AYANAMI-AGENT/
├── backend/
│   ├── src/
│   │   ├── dev_agent/              # Core backend logic and agents
│   │   │   ├── agents/             # Modular AI agents (GitHub, Email, Anime)
│   │   │   ├── api/                # FastAPI application and routes
│   │   │   ├── core/               # Core utilities and models
│   │   │   ├── database/           # MongoDB connection and models
│   │   │   ├── orchestrator/       # Agent dispatching and planning
│   │   │   ├── tools/              # External tool integrations (GitHub, Email)
│   │   │   └── ...
│   │   └── ...
│   ├── pyproject.toml              # Backend project metadata and dependencies
│   ├── requirements.txt            # Python dependencies
│   └── ...
├── frontend/
│   ├── app/                        # Next.js application pages
│   ├── components/                 # Reusable React components
│   ├── public/                     # Static assets (images, cursors)
│   ├── package.json                # Frontend project metadata and dependencies
│   ├── next.config.mjs             # Next.js configuration
│   └── ...
├── .env.example                    # Example environment variables
├── .gitignore                      # Git ignore file
└── vercel.json                     # Vercel deployment configuration
```

### 🧠 What I Learned

-   **Modular AI Agent Design:** Implementing a flexible and extensible architecture for AI agents, allowing for easy integration of new functionalities.
-   **Full-stack Integration:** Seamlessly connecting a FastAPI backend with a Next.js/React frontend, managing API interactions and data flow.
-   **LLM Orchestration:** Utilizing Groq for efficient and fast language model processing within agent workflows.
-   **External API Integration:** Developing robust connectors for services like GitHub and Google (Email) to extend agent capabilities.
-   **Thematic Design Implementation:** Incorporating a distinct aesthetic (Evangelion/Rei Ayanami) into both the functional and visual aspects of the project.

### 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 📧 Contact

Eduardo Carvalho - [GitHub](https://github.com/EduhxH)

### Tags

`ai-agent` `fastapi` `nextjs` `react` `python` `typescript` `developer-tools` `automation` `github-api` `email-automation` `llm` `groq` `mongodb` `evangelion` `rei-ayanami` `productivity` `ai` `agent-system` `fullstack` `web-development`

# AYANAMI-AGENT

![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white) ![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black) ![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

## 🤖 Intelligent AI Agent System Inspired by Evangelion

AYANAMI-AGENT is a sophisticated AI agent system designed to streamline development workflows and provide intelligent assistance. Inspired by the iconic character Rei Ayanami from Neon Genesis Evangelion, this project combines cutting-edge AI capabilities with a sleek, minimalist interface to create a powerful and intuitive tool for developers.

## ✨ Features

### Backend (Python - FastAPI)

-   **Modular Agent Architecture:** Easily extendable system with specialized agents for various tasks.
-   **GitHub Agent:** Analyzes repositories, identifies issues, and provides suggestions for code quality and improvements.
-   **Email Agent:** Manages email interactions, automates responses, and helps organize communication.
-   **Anime Agent (Easter Egg):** A unique feature that recommends anime based on a developer's technical profile, offering technical and cultural justifications.
-   **Robust API:** Built with FastAPI for high performance, automatic documentation, and easy integration.
-   **MongoDB Integration:** Utilizes MongoDB for flexible and scalable data storage.
-   **LLM Integration:** Leverages Groq for fast and efficient language model interactions.

### Frontend (Next.js - React)

-   **Intuitive User Interface:** A clean and modern web interface built with Next.js and React, inspired by minimalist design principles.
-   **Real-time Interactions:** Seamless communication with the backend agents for dynamic responses and updates.
-   **Responsive Design:** Optimized for various screen sizes, ensuring a consistent experience across devices.
-   **Themed Cursors:** Custom cursors inspired by the Evangelion aesthetic, enhancing the user experience.

## 🚀 Getting Started

To get AYANAMI-AGENT up and running locally, follow these steps:

### Prerequisites

-   Python 3.11+
-   Node.js 18+
-   pnpm (recommended package manager for frontend)
-   MongoDB instance (local or cloud-hosted)
-   Groq API Key
-   GitHub Personal Access Token (for GitHub Agent functionality)
-   Google API Credentials (for Email Agent functionality)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/EduhxH/AYANAMI-AGENT.git
    cd AYANAMI-AGENT
    ```

2.  **Backend Setup:**

    ```bash
    cd backend
    pip install -r requirements.txt
    # Create a .env file based on .env.example and fill in your credentials
    # cp .env.example .env
    uvicorn dev_agent.api.app:app --reload
    ```

3.  **Frontend Setup:**

    ```bash
    cd ../frontend
    pnpm install
    # Create a .env.local file based on .env.example and fill in your credentials
    # cp .env.example .env.local
    pnpm dev
    ```

## ⚙️ Configuration

Both the `backend` and `frontend` directories contain `.env.example` files. Copy these to `.env` (for backend) and `.env.local` (for frontend) respectively, and populate them with your API keys and other necessary configurations.

## 📸 Preview

*(Placeholder for a GIF or screenshot of the agent in action)*

## 💡 Inspiration

This project draws heavy inspiration from the aesthetic and thematic elements of **Neon Genesis Evangelion**, particularly the character **Rei Ayanami**. The goal is to create an agent that is not only highly functional but also embodies a sense of calm efficiency and profound capability, much like its namesake.

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

Eduardo Carvalho - [GitHub](https://github.com/EduhxH)

## Tags

`ai-agent` `fastapi` `nextjs` `react` `python` `typescript` `developer-tools` `automation` `github-api` `email-automation` `llm` `groq` `mongodb` `evangelion` `rei-ayanami` `productivity`

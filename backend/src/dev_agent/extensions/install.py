"""
Regista o General Conversation Agent e melhora o planner/dispatcher via monkey-patch.

MCP-SERVER-PRO (github.com/EduhxH/MCP-SERVER-PRO) não é integrado aqui:
- Gmail/GitHub já existem nativamente no Dev Agent
- Pinecone/Excel/IDE são para clientes MCP (stdio), não para esta API REST
- Autonomy tools são heurísticas em memória sem valor claro face ao orchestrator actual
- Não inclui web search — usamos Groq Compound (GROQ_API_KEY) para pesquisa ao vivo
"""

import json
from typing import List

from dev_agent.core.models import AgentResult, AgentType
from dev_agent.extensions.agents.general_agent import GeneralConversationAgent

_agent_extensions_installed = False


def install_agent_extensions() -> None:
    global _agent_extensions_installed
    if _agent_extensions_installed:
        return

    _patch_planner()
    _patch_dispatcher()
    _patch_orchestrator_summary()

    _agent_extensions_installed = True


def _patch_planner() -> None:
    from dev_agent.orchestrator.planner import Planner

    if getattr(Planner, "_general_patch_installed", False):
        return

    _original = Planner.decide_agents

    async def decide_agents_extended(self, query: str) -> List[AgentType]:
        from groq import AsyncGroq
        from dev_agent.core.config import get_settings
        from dev_agent.preferences.context import with_system_preamble

        settings = get_settings()
        client = AsyncGroq(api_key=settings.groq_api_key)

        prompt = f"""
Analisa o pedido e escolhe quais agentes activar.

Pedido: "{query}"

Agentes:
- "github": código, repositórios, PRs, commits (requer repo/GitHub explícito)
- "email": para ler/resumir Gmail, redigir ou enviar emails, draft/rascunhos e sugestões de resposta (requer email ou intenção de mensagem explícita)
- "anime": APENAS se pedir recomendações de anime
- "general": conversa geral, saudações, factos, tutoriais, pesquisa, opiniões, "o que é", "como funciona", qualquer coisa SEM GitHub/Gmail

Regras:
- Usa UM agente na maioria dos casos
- "general" é o fallback por defeito
- Não uses "github" só porque o utilizador disse "repositório" sem nome de repo ligado ao GitHub
- Não uses "email" sem pedido claro de email/Gmail

Responde APENAS JSON: {{"agents": ["general"]}}
"""

        messages = with_system_preamble([{"role": "user", "content": prompt}])

        try:
            response = await client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=0.1,
            )
            content = response.choices[0].message.content.strip()
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)
            agents = [AgentType(a) for a in data["agents"]]
            if agents:
                return _sanitize_agents(agents, query)
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

        return _keyword_fallback(query)

    Planner.decide_agents = decide_agents_extended
    Planner._general_patch_installed = True


def _sanitize_agents(agents: List[AgentType], query: str) -> List[AgentType]:
    """Evita activar github/email quando o pedido é claramente geral."""
    q = query.lower()
    if AgentType.GENERAL in agents and len(agents) == 1:
        return agents

    github_signals = ("github.com", "owner/", "pull request", "pr #", "commit")
    email_signals = ("gmail", "email", "e-mail", "inbox", "correio", "mensagem", "mail")
    email_actions = ("responda", "responder", "responde", "envie", "enviar", "mande", "mandar", "envio", "escreva", "escrever")
    email_objects = ("rascunho", "draft", "sugestão", "sugestao", "resposta", "mensagem")

    wants_github = any(s in q for s in ("repo", "repositório", "repositorio", "código", "codigo", "pr ", "github"))
    wants_github = wants_github or any(s in q for s in github_signals)
    wants_email = any(s in q for s in email_signals) or (
        any(s in q for s in email_actions)
        and any(s in q for s in email_objects)
    )

    if AgentType.GITHUB in agents and not wants_github:
        agents = [a for a in agents if a != AgentType.GITHUB]
    if AgentType.EMAIL in agents and not wants_email:
        agents = [a for a in agents if a != AgentType.EMAIL]

    if not agents:
        return [AgentType.GENERAL]
    return agents


def _keyword_fallback(query: str) -> List[AgentType]:
    """Espelha o fallback do planner original, com GENERAL em vez de GITHUB por defeito."""
    q = query.lower()
    if any(w in q for w in ("anime", "manga")) and "recomend" in q:
        return [AgentType.ANIME]
    github_words = (
        "github.com",
        "pull request",
        "commit",
        "repositório",
        "repositorio",
        "repo",
        "código",
        "codigo",
        "github",
        " pr ",
        "prs",
    )
    if any(w in q for w in github_words):
        return [AgentType.GITHUB]
    if any(
        w in q
        for w in ("gmail", "email", "e-mail", "inbox", "correio", "mensagem", "mail")
    ):
        return [AgentType.EMAIL]
    if any(w in q for w in ("envie", "enviar", "mande", "mandar", "envio")) and any(
        w in q
        for w in ("rascunho", "draft", "sugestão", "sugestao", "resposta", "mensagem", "sugestão de email", "sugestao de email")
    ):
        return [AgentType.EMAIL]
    return [AgentType.GENERAL]


def _patch_dispatcher() -> None:
    from dev_agent.orchestrator.dispatcher import Dispatcher

    if getattr(Dispatcher, "_general_patch_installed", False):
        return

    _original_get = Dispatcher._get_agent

    def _get_agent_extended(self, agent_type: AgentType):
        if agent_type == AgentType.GENERAL:
            return GeneralConversationAgent()
        return _original_get(self, agent_type)

    Dispatcher._get_agent = _get_agent_extended
    Dispatcher._general_patch_installed = True


def _patch_orchestrator_summary() -> None:
    from dev_agent.orchestrator.orchestrator import Orchestrator

    if getattr(Orchestrator, "_general_summary_patch_installed", False):
        return

    _original_summary = Orchestrator._generate_summary

    async def generate_summary_extended(self, query: str, results: List[AgentResult]) -> str:
        if _is_general_only_success(results):
            return results[0].data.get("answer", "")

        if _general_among_results(results):
            general = next(
                r for r in results if r.agent == AgentType.GENERAL and r.success
            )
            others = [r for r in results if r.agent != AgentType.GENERAL]
            if not others:
                return general.data.get("answer", "")
            if all(not r.success for r in others):
                return general.data.get("answer", "")

        return await _original_summary(self, query, results)

    Orchestrator._generate_summary = generate_summary_extended
    Orchestrator._general_summary_patch_installed = True


def _is_general_only_success(results: List[AgentResult]) -> bool:
    return (
        len(results) == 1
        and results[0].agent == AgentType.GENERAL
        and results[0].success
        and results[0].data.get("answer")
    )


def _general_among_results(results: List[AgentResult]) -> bool:
    return any(
        r.agent == AgentType.GENERAL and r.success and r.data.get("answer")
        for r in results
    )

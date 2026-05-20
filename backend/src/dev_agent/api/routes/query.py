from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List

from dev_agent.core.models import TaskRequest, AgentType
from dev_agent.orchestrator.orchestrator import Orchestrator
from dev_agent.api.dependencies import get_current_user
from dev_agent.auth.google_tokens import ensure_fresh_google_token
from dev_agent.database.connection import get_database
from dev_agent.database.repositories.users import UsersRepository
from dev_agent.database.repositories.chat_messages import ChatMessagesRepository

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    query: str
    agents: Optional[List[AgentType]] = None


@router.post("/")
async def handle_query(
    body: QueryRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    print("=" * 80)
    print("[ROUTE /query/] Nova requisição recebida")
    print(f"[ROUTE /query/] Query: {body.query!r}")
    print(f"[ROUTE /query/] User: {current_user.email} (id={current_user.id})")
    print(f"[ROUTE /query/] Agentes forçados: {body.agents}")
    print("=" * 80)
    
    users_repo = UsersRepository(db)
    chat_messages_repo = ChatMessagesRepository(db)

    # Buscar usuário atualizado do banco de dados para garantir tokens recentes
    user = await users_repo.find_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizador não encontrado na sessão",
        )

    print(f"[ROUTE /query/] Usuário atualizado do BD:")
    print(f"  - github_token: {'***' if user.github_token else 'NULL'}")
    print(f"  - github_username: {user.github_username}")

    # Gravar a nova mensagem do utilizador assim que ela chega
    await chat_messages_repo.save_message(user_id=user.id, role="user", content=body.query)

    # Puxar as últimas 10 mensagens do histórico desse utilizador antes de chamar o Orquestrador
    # Como acabámos de gravar a mensagem do utilizador, a mais recente (índice 0) é a atual.
    # Queremos apenas as 10 mensagens anteriores como contexto histórico.
    all_history = await chat_messages_repo.get_history(user_id=user.id, limit=11)
    history = all_history[1:11]

    async def refresh_google() -> str:
        refreshed_user = await users_repo.find_by_id(user.id)
        if not refreshed_user:
            return ""
        refreshed = await ensure_fresh_google_token(refreshed_user, users_repo)
        return refreshed or refreshed_user.google_token or ""

    user_data = {
        "user_id": user.id,
        "github_token": user.github_token,
        "github_username": user.github_username,
        "google_token": user.google_token,
    }

    orchestrator = Orchestrator(on_google_token_refresh=refresh_google)
    task = TaskRequest(
        query=body.query,
        user_id=user.id,
        agents=body.agents,
    )

    result = await orchestrator.handle(task, user_data, history=history)

    # Garante que a resposta final gerada pelo agente também seja guardada na BD com a role 'assistant'
    agents_used = [r.agent.value for r in result.results]
    await chat_messages_repo.save_message(
        user_id=user.id,
        role="assistant",
        content=result.summary,
        agent_used=agents_used
    )

    return result

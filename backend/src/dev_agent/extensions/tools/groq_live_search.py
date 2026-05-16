"""
Pesquisa web ao vivo via Groq Compound — usa apenas GROQ_API_KEY.
Modelos: groq/compound-mini (rápido) ou groq/compound (mais completo).
"""

from typing import Any, Optional

from groq import APIStatusError, AsyncGroq

from dev_agent.preferences.context import with_system_preamble

# Apenas pedidos claramente "ao minuto" — termos genéricos como "notícias"
# disparam compound-mini para evitar erro 413 (payload too large).
_LIVE_HINTS = (
    "ultima hora",
    "última hora",
    "breaking",
    "ao vivo",
    "em tempo real",
    "agora mesmo",
    "right now",
    "just now",
    "ultimas noticias",
    "últimas notícias",
    "latest news",
    "live update",
)

COMPOUND_MINI = "groq/compound-mini"


def infer_search_country(query: str, override: Optional[str]) -> Optional[str]:
    if override and override.strip():
        return override.strip().lower()
    lower = query.lower()
    pt_markers = (
        "olá",
        "ola",
        "portugal",
        "português",
        "portugues",
        "lisboa",
        "brasil",
        "notícias",
        "noticias",
        "hoje",
        "última",
        "ultima",
    )
    if any(m in lower for m in pt_markers):
        return "portugal"
    return None


def pick_search_model(
    query: str,
    *,
    default_model: str,
    live_model: str,
) -> str:
    q = query.lower()
    if any(h in q for h in _LIVE_HINTS):
        return live_model
    return default_model


def is_payload_too_large(exc: BaseException) -> bool:
    if isinstance(exc, APIStatusError) and getattr(exc, "status_code", None) == 413:
        return True
    msg = str(exc).lower()
    return (
        "413" in msg
        or "payload too large" in msg
        or "request entity too large" in msg
    )


def _search_models_to_try(primary: str, *, mini_model: str = COMPOUND_MINI) -> list[str]:
    ordered: list[str] = []
    for m in (primary, mini_model):
        if m and m not in ordered:
            ordered.append(m)
    return ordered


async def answer_with_live_search(
    client: AsyncGroq,
    query: str,
    *,
    model: str,
    country: Optional[str] = None,
    language_hint: str = "the user's language",
    mini_fallback_model: str = COMPOUND_MINI,
) -> tuple[str, bool]:
    """
    Uma chamada ao Compound: o modelo decide pesquisar e sintetiza com citações.
    Em 413, repete com compound-mini (payload menor).
    Devolve (resposta, pesquisa_executada).
    """
    last_error: Optional[BaseException] = None

    for attempt_model in _search_models_to_try(model, mini_model=mini_fallback_model):
        try:
            return await _answer_with_live_search_once(
                client,
                query,
                model=attempt_model,
                country=country,
                language_hint=language_hint,
            )
        except Exception as exc:
            if is_payload_too_large(exc):
                last_error = exc
                continue
            raise

    if last_error:
        raise last_error
    return "", False


async def _answer_with_live_search_once(
    client: AsyncGroq,
    query: str,
    *,
    model: str,
    country: Optional[str] = None,
    language_hint: str = "the user's language",
) -> tuple[str, bool]:
    user_content = f"""User request:
{query}

Instructions:
- Use web search for up-to-date facts when needed.
- Reply in {language_hint}.
- Be short and direct unless the user asks for detail.
- Include sources or citations when available."""

    # Compound não precisa do preamble AYANAMI — reduz tokens no pedido.
    messages = [{"role": "user", "content": user_content}]

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.35,
    }
    if country:
        kwargs["search_settings"] = {"country": country}

    response = await client.chat.completions.create(**kwargs)
    msg = response.choices[0].message
    answer = (msg.content or "").strip()
    used_search = bool(msg.executed_tools)
    return answer, used_search

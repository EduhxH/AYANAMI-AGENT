"""Contexto por pedido para o preamble AYANAMI (usado pelos hooks)."""

from contextvars import ContextVar
from typing import List, Optional

_preamble: ContextVar[Optional[str]] = ContextVar("ayanami_preamble", default=None)


def set_preamble(text: Optional[str]) -> None:
    _preamble.set(text)


def get_preamble() -> Optional[str]:
    return _preamble.get()


def with_system_preamble(messages: List[dict]) -> List[dict]:
    """Prepend ou funde o preamble nas mensagens Groq."""
    preamble = get_preamble()
    if not preamble:
        return messages

    out = list(messages)
    if out and out[0].get("role") == "system":
        out[0] = {
            "role": "system",
            "content": f"{preamble}\n\n{out[0]['content']}",
        }
    else:
        out.insert(0, {"role": "system", "content": preamble})
    return out

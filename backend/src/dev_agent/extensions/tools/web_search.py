"""
Fallback: Tavily ou SerpAPI (opcional). Pesquisa principal = Groq Compound (groq_live_search.py).
"""

import os
from typing import Any

import httpx


def legacy_search_configured() -> bool:
    return bool(os.getenv("TAVILY_API_KEY") or os.getenv("SERPAPI_API_KEY"))


def search_configured() -> bool:
    """True se Groq API key existe (Compound) ou fallback Tavily/SerpAPI."""
    # Nota: Groq api_key é verificado via settings/config, não aqui
    return legacy_search_configured()


async def search_web(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if tavily_key:
        return await _search_tavily(query, tavily_key, max_results)

    serp_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if serp_key:
        return await _search_serpapi(query, serp_key, max_results)

    return []


async def _search_tavily(
    query: str, api_key: str, max_results: int
) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "include_answer": True,
            },
        )
        if response.status_code != 200:
            raise ValueError(f"Tavily error {response.status_code}: {response.text[:200]}")

        data = response.json()
        results: list[dict[str, Any]] = []
        answer = data.get("answer")
        if answer:
            results.append(
                {
                    "title": "Tavily summary",
                    "url": "",
                    "snippet": answer,
                }
            )
        for item in data.get("results", [])[:max_results]:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", item.get("snippet", "")),
                }
            )
        return results


async def _search_serpapi(
    query: str, api_key: str, max_results: int
) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            "https://serpapi.com/search",
            params={
                "api_key": api_key,
                "engine": "google",
                "q": query,
                "num": max_results,
            },
        )
        if response.status_code != 200:
            raise ValueError(f"SerpAPI error {response.status_code}: {response.text[:200]}")

        data = response.json()
        organic = data.get("organic_results", [])[:max_results]
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            }
            for item in organic
        ]


def format_search_results(results: list[dict[str, Any]]) -> str:
    if not results:
        return ""
    lines = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "Result")
        snippet = (r.get("snippet") or "")[:500]
        url = r.get("url", "")
        block = f"{i}. {title}\n{snippet}"
        if url:
            block += f"\nSource: {url}"
        lines.append(block)
    return "\n\n".join(lines)

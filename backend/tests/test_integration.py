"""Integration tests for critical Dispatcher and EmailAgent flows."""

from __future__ import annotations

from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dev_agent.agents.email_agent import EmailAgent
from dev_agent.core.models import AgentResult, AgentType
from dev_agent.orchestrator.dispatcher import Dispatcher


@pytest.mark.asyncio
async def test_github_email_dependency_chain(user_data):
    """GitHubAgent runs first, context is injected, then EmailAgent runs."""
    call_order: List[str] = []
    github_summary_at_email_run = None

    gh_result = AgentResult(
        agent=AgentType.GITHUB,
        success=True,
        data={
            "repositories": ["EduhxH/AYANAMI-AGENT"],
            "repo_context_text": "test summary",
        },
    )
    email_result = AgentResult(
        agent=AgentType.EMAIL,
        success=True,
        data={"action": "send"},
    )

    mock_github_agent = MagicMock()
    mock_github_agent.run = AsyncMock(
        side_effect=lambda query, history=None: (
            call_order.append("github") or gh_result
        )
    )

    mock_email_agent = MagicMock()

    async def email_run(query, history=None):
        nonlocal github_summary_at_email_run
        call_order.append("email")
        github_summary_at_email_run = mock_email_agent.github_summary
        return email_result

    mock_email_agent.run = AsyncMock(side_effect=email_run)

    def fake_get_agent(agent_type: AgentType):
        if agent_type == AgentType.GITHUB:
            return mock_github_agent
        if agent_type == AgentType.EMAIL:
            return mock_email_agent
        return None

    dispatcher = Dispatcher(user_data)
    with patch.object(dispatcher, "_get_agent", side_effect=fake_get_agent):
        results = await dispatcher.run(
            "envie um email com resumo do github para eduardo@example.com",
            [AgentType.GITHUB, AgentType.EMAIL],
        )

    assert call_order == ["github", "email"]
    assert github_summary_at_email_run == "test summary"
    assert len(results) == 2
    assert all(r.success for r in results)
    assert results[0].agent == AgentType.GITHUB
    assert results[1].agent == AgentType.EMAIL
    mock_github_agent.run.assert_awaited_once()
    mock_email_agent.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_dispatcher_short_circuits_on_github_failure(user_data):
    """When GitHub fails, EmailAgent.run() is never called."""
    gh_failure = AgentResult(
        agent=AgentType.GITHUB,
        success=False,
        data={},
        error="API timeout",
    )

    mock_github_agent = MagicMock()
    mock_github_agent.run = AsyncMock(return_value=gh_failure)

    mock_email_agent = MagicMock()
    mock_email_agent.run = AsyncMock()

    def fake_get_agent(agent_type: AgentType):
        if agent_type == AgentType.GITHUB:
            return mock_github_agent
        if agent_type == AgentType.EMAIL:
            return mock_email_agent
        return None

    dispatcher = Dispatcher(user_data)
    with patch.object(dispatcher, "_get_agent", side_effect=fake_get_agent):
        results = await dispatcher.run(
            "envie um email com resumo do github",
            [AgentType.GITHUB, AgentType.EMAIL],
        )

    mock_email_agent.run.assert_not_awaited()

    email_results = [r for r in results if r.agent == AgentType.EMAIL]
    assert len(email_results) == 1
    email_result = email_results[0]
    assert email_result.success is False
    assert email_result.error is not None
    assert "GitHub" in email_result.error or "github" in email_result.error.lower()
    assert "API timeout" in email_result.error


@pytest.mark.asyncio
async def test_email_classifier_handles_empty_groq_response(settings_mock):
    """Empty Groq content returns None and logs last_raw_response."""
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content=""))]

    mock_groq = MagicMock()
    mock_groq.chat.completions.create = AsyncMock(return_value=mock_completion)

    with patch("dev_agent.agents.email_agent.get_settings", return_value=settings_mock), \
         patch("dev_agent.agents.email_agent.AsyncGroq", return_value=mock_groq), \
         patch("dev_agent.agents.email_agent.logger") as mock_logger:

        agent = EmailAgent(token="fake-token")
        result = await agent._classify("envie um email para joao@example.com")

    assert result is None
    mock_logger.error.assert_called_once()
    format_msg = mock_logger.error.call_args[0][0]
    logged_raw = mock_logger.error.call_args[0][1]
    assert "last_raw_response" in format_msg
    assert logged_raw == ""


@pytest.mark.asyncio
async def test_email_classifier_forces_json_object_format(settings_mock):
    """_classify() requests JSON object mode from the Groq API."""
    valid_json = (
        '{"intent": "read", "recipient": null, "subject": null, '
        '"body": null, "reasoning": "User wants to read inbox."}'
    )
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content=valid_json))]

    mock_groq = MagicMock()
    mock_groq.chat.completions.create = AsyncMock(return_value=mock_completion)

    with patch("dev_agent.agents.email_agent.get_settings", return_value=settings_mock), \
         patch("dev_agent.agents.email_agent.AsyncGroq", return_value=mock_groq):

        agent = EmailAgent(token="fake-token")
        result = await agent._classify("mostra os meus emails recentes")

    assert result is not None
    assert result.intent == "read"
    mock_groq.chat.completions.create.assert_awaited()
    call_kwargs = mock_groq.chat.completions.create.await_args.kwargs
    assert call_kwargs.get("response_format") == {"type": "json_object"}

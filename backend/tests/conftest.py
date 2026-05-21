"""Shared pytest fixtures and path setup for backend integration tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = BACKEND_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture
def user_data() -> Dict[str, Any]:
    return {
        "user_id": "test-user",
        "github_token": "fake-github-token",
        "github_username": "EduhxH",
        "google_token": "fake-google-token",
    }


@pytest.fixture
def settings_mock() -> MagicMock:
    mock = MagicMock()
    mock.groq_api_key = "fake-groq-key"
    mock.groq_model = "llama-3.3-70b-versatile"
    return mock

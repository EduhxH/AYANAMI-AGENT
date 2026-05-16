"""
Registo de extensões (preferências, uploads, hooks).
Importar e chamar register_extensions(app) a partir de app.py — apenas código aditivo.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from dev_agent.api.routes import preferences as preferences_routes
from dev_agent.database.connection import get_database
from dev_agent.database.repositories.user_preferences import UserPreferencesRepository
from dev_agent.preferences.hooks import install_orchestrator_hooks
from dev_agent.preferences.storage import get_upload_root
from dev_agent.extensions.install import install_agent_extensions


def register_extensions(app: FastAPI) -> None:
    app.include_router(preferences_routes.router)
    install_orchestrator_hooks()
    install_agent_extensions()

    upload_root = get_upload_root()
    uploads_parent = upload_root.parent
    uploads_parent.mkdir(parents=True, exist_ok=True)

    app.mount(
        "/uploads",
        StaticFiles(directory=str(uploads_parent)),
        name="uploads",
    )

    @app.on_event("startup")
    async def _ensure_preferences_indexes() -> None:
        db = get_database()
        await UserPreferencesRepository(db).ensure_indexes()

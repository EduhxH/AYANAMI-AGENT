from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dev_agent.core.config import get_settings
from dev_agent.database.connection import connect_to_mongodb, close_mongodb_connection
from dev_agent.api.routes import auth, query, health, anime

settings = get_settings()

app = FastAPI(
    title="Dev Agent API",
    version="1.0.0",
    docs_url="/docs",  
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown():
    await close_mongodb_connection()

# Registar rotas
app.include_router(auth.router)
app.include_router(query.router)
app.include_router(health.router)
app.include_router(anime.router)

from dev_agent.bootstrap import register_extensions

register_extensions(app)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dev_agent.core.config import get_settings
from dev_agent.database.connection import connect_to_mongodb, close_mongodb_connection
from dev_agent.api.routes import auth, query, health, anime
from dev_agent.bootstrap import register_extensions

settings = get_settings()

app = FastAPI(
    title="Dev Agent API",
    version="1.0.0",
    docs_url="/docs",  
)

@app.on_event("startup")
async def startup():
    await connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown():
    await close_mongodb_connection()

# 1. Registar rotas normais
app.include_router(auth.router)
app.include_router(query.router)
app.include_router(health.router)
app.include_router(anime.router)

# 2. Registar extensões do bootstrap (executado ANTES do CORS)
register_extensions(app)

# 3. CORSMiddleware deve ser adicionado em ÚLTIMO lugar
# Adicionámos "*" temporariamente para garantir que nada bloqueia os teus testes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*", 
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
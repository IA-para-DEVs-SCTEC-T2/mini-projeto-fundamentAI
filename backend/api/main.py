"""
Entry point da API FastAPI do FundamentAI.

Inicializa a aplicação, registra as rotas e configura o banco de dados.

Para rodar localmente:
    uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

Documentação interativa disponível em:
    http://localhost:8000/docs  (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.analysis import router as analysis_router
from backend.api.routes.ticker import router as ticker_router
from backend.db.models import create_tables

# ---------------------------------------------------------------------------
# Configuração de logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Inicialização da aplicação
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FundamentAI API",
    description=(
        "API do Analisador Fundamentalista de Ações da B3. "
        "Consolida dados financeiros públicos e gera análises estruturadas "
        "com viés educativo via Anthropic Claude."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — permite requisições do frontend React
# ---------------------------------------------------------------------------

_ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173",  # React dev servers
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

app.include_router(ticker_router)
app.include_router(analysis_router)


# ---------------------------------------------------------------------------
# Eventos de ciclo de vida
# ---------------------------------------------------------------------------


@app.on_event("startup")
def on_startup() -> None:
    """Inicializa o banco de dados na inicialização da API."""
    logger.info("Iniciando FundamentAI API v%s", app.version)
    create_tables()
    logger.info("Banco de dados inicializado")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """
    Verifica se a API está operacional.

    Returns:
        Status da API e versão.
    """
    return {
        "status": "ok",
        "version": app.version,
        "service": "FundamentAI API",
    }


@app.get("/", tags=["root"])
def root() -> dict:
    """Redireciona para a documentação."""
    return {
        "message": "FundamentAI API",
        "docs": "/docs",
        "health": "/health",
    }

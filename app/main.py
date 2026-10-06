from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.endpoints import limiter
from app.api.v1.endpoints import router as api_router

app = FastAPI(
    title="BuscaFri API",
    description="API de Consulta & Analytics CNPJ",
    version="1.0.0",
)

# Configuração do Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Inclui as rotas de busca
app.include_router(api_router, prefix="/api/v1", tags=["Busca"])


@app.get("/")
def read_root():
    return {
        "message": "Bem-vindo ao BuscaFri - API de Consulta CNPJ",
        "status": "Executando na VPS Google Cloud (GCP)",
        "docs": "/docs",
        "health": "/health",
        "author": "Victor Araujo Barros",
    }


@app.get("/health")
def health_check():
    return {"status": "online", "message": "BuscaFri API esta rodando liso"}

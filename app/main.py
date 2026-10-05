from fastapi import FastAPI

app = FastAPI(
    title="BuscaFri API",
    description="API de Consulta & Analytics CNPJ",
    version="1.0.0",
)


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

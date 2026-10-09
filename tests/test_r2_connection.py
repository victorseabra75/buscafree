import os

import pytest

from app.core.database import db_client

# Verifica se as credenciais reais do R2 estão disponíveis e não vazias/espaços
has_r2_creds = all(
    (val := os.getenv(var)) and val.strip()
    for var in [
        "R2_ACCOUNT_ID",
        "R2_TOKEN_VALUE",
        "R2_ACCESS_KEY_ID",
        "R2_SECRET_ACCESS_KEY",
    ]
)

# Se não temos credenciais reais, pulamos os testes de integração
pytestmark = pytest.mark.skipif(
    not has_r2_creds,
    reason="Credenciais R2 não configuradas, pulando teste de integração",
)


@pytest.mark.integration
def test_r2_duckdb_connection_and_schemas():
    """Testa a conexão do DuckDB com o Cloudflare R2 e inspeciona as tabelas"""
    # Garante que o cliente está conectado
    if db_client.conn is None:
        db_client.connect()

    assert db_client.conn is not None, "Falha ao conectar no DuckDB"

    pastas = [
        "cnaes",
        "empresas",
        "estabelecimentos",
        "motivos",
        "municipios",
        "naturezas",
        "paises",
        "qualificacoes",
        "simples",
        "socios",
    ]

    for pasta in pastas:
        path = f"s3://buscafri-data/{pasta}/*.parquet"
        # Tenta ler o schema e as primeiras 5 linhas de cada pasta do R2
        schema_df = db_client.query(f"DESCRIBE SELECT * FROM '{path}'")
        assert not schema_df.empty, f"Schema vazio para {pasta}"

        df = db_client.query(f"SELECT * FROM '{path}' LIMIT 5")
        # Valida se executou com sucesso (pode vir vazio se o bucket estiver sem dados na pasta específica)
        assert df is not None

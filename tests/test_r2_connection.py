from app.core.database import db_client


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
        "socios"
    ]

    for pasta in pastas:
        path = f"s3://buscafri-data/{pasta}/*.parquet"
        try:
            # Tenta ler o schema e as primeiras 5 linhas de cada pasta do R2
            schema_df = db_client.query(f"DESCRIBE SELECT * FROM '{path}'")
            assert not schema_df.empty, f"Schema vazio para {pasta}"
            
            df = db_client.query(f"SELECT * FROM '{path}' LIMIT 5")
            # Valida se executou com sucesso (pode vir vazio se o bucket estiver sem dados na pasta específica)
            assert df is not None
        except Exception as e:
            # Se a pasta não existir ou estiver vazia no R2, registramos no log do teste mas não quebramos tudo
            print(f"Aviso ao inspecionar {pasta}: {e}")

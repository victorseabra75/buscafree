from pathlib import Path

import duckdb
import pandas as pd

from app.core.database import db_client

PASTAS = [
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

OUTPUT = Path("data/schema/mapeamento_cnpj.csv")


def analisar_schema(pasta: str) -> pd.DataFrame:
    path = f"s3://buscafri-data/{pasta}/*.parquet"

    print(f"Analisando: {pasta}...")

    try:
        schema = db_client.query(f"DESCRIBE SELECT * FROM '{path}'")

        if schema.empty:
            print(f"  Nenhuma coluna encontrada em {pasta}.")
            return pd.DataFrame()

        schema.insert(0, "pasta", pasta)

        print(f"  {len(schema)} colunas encontradas.")

        return schema

    except duckdb.Error as exc:
        print(f"  ERRO DUCKDB: {exc}")
        return pd.DataFrame()


def main() -> None:
    print("MAPEAMENTO DE SCHEMAS — BUSCAFRI / CNPJ")
    print("=" * 80)

    if db_client.conn is None:
        db_client.connect()

    if db_client.conn is None:
        raise RuntimeError("Não foi possível conectar ao DuckDB.")

    schemas = []

    for pasta in PASTAS:
        schema = analisar_schema(pasta)

        if not schema.empty:
            schemas.append(schema)

    if not schemas:
        raise RuntimeError("Nenhum schema foi encontrado.")

    resultado = pd.concat(schemas, ignore_index=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 80)
    print(f"Total de colunas mapeadas: {len(resultado)}")
    print(f"Arquivo gerado: {OUTPUT}")
    print("=" * 80)


if __name__ == "__main__":
    main()

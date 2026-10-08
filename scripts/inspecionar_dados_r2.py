import duckdb

from app.core.database import db_client


def diagnosticar_tabela(tabela: str) -> None:
    path = f"s3://buscafri-data/{tabela}/*.parquet"

    print("\n" + "#" * 50)
    print(f"DIAGNÓSTICO DA TABELA: {tabela}")
    print("#" * 50)

    try:
        # DESCRIBE
        res = db_client.query(f"DESCRIBE SELECT * FROM '{path}'")
        print(f"\nDEBUG: Tipo do resultado: {type(res)}")

        # O resultado do DuckDB .query() parece ser um DataFrame do Pandas
        desc = res
        print("\n--- DESCRIBE ---")
        print(desc.to_string())

        # COLUNAS (nomes)
        colunas = desc["column_name"].tolist()
        print("\n--- NOMES DAS COLUNAS ---")
        print(colunas)

        # AMOSTRA
        print("\n--- PRIMEIRAS 3 LINHAS ---")
        df = db_client.query(f"SELECT * FROM '{path}' LIMIT 3")
        print(df.to_string().encode("utf-8", "replace").decode("utf-8"))

    except duckdb.Error as exc:
        print(f"\nERRO AO DIAGNOSTICAR {tabela}: {exc}")


def main() -> None:
    if db_client.conn is None:
        db_client.connect()

    if db_client.conn is None:
        raise RuntimeError("Não foi possível conectar ao DuckDB.")

    tab_list = ["empresas", "estabelecimentos", "simples", "socios"]
    for tabela in tab_list:
        diagnosticar_tabela(tabela)


if __name__ == "__main__":
    main()

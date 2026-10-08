from pathlib import Path

import duckdb

# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(r"C:\Users\victo\Desktop\BUSCACNPJ")

INPUT_DIR = BASE_DIR / "data" / "processed_corrigido" / "estabelecimentos"

OUTPUT_DIR = BASE_DIR / "data" / "particionado" / "estabelecimentos"


# ============================================================
# FUNÇÃO AUXILIAR
# ============================================================


def get_count(con, query):
    """
    Executa uma consulta COUNT(*) e retorna o valor.

    A verificação de None evita o erro:
    Object of type "None" is not subscriptable
    """

    result = con.execute(query).fetchone()

    if result is None:
        raise RuntimeError("O DuckDB não retornou resultado para a consulta COUNT.")

    return result[0]


# ============================================================
# PARTICIONAMENTO
# ============================================================


def run_partitioning():

    print("=" * 70)
    print("PARTICIONAMENTO DA TABELA ESTABELECIMENTOS")
    print("=" * 70)

    print("\nIniciando particionamento da tabela estabelecimentos por UF...")

    # --------------------------------------------------------
    # Garantir diretório de saída
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Verificar arquivos de entrada
    # --------------------------------------------------------

    input_files = list(INPUT_DIR.glob("*.parquet"))

    if not input_files:
        raise FileNotFoundError(f"Nenhum arquivo Parquet encontrado em:\n{INPUT_DIR}")

    print(f"\nArquivos encontrados na origem: {len(input_files)}")

    # --------------------------------------------------------
    # DuckDB
    # --------------------------------------------------------

    con = duckdb.connect()

    try:
        input_path = str(INPUT_DIR / "*.parquet").replace("\\", "/")

        output_path = str(OUTPUT_DIR).replace("\\", "/")

        # ====================================================
        # 1. TOTAL DE LINHAS NA ORIGEM
        # ====================================================

        print("\n--- CONTAGEM DA ORIGEM ---")

        orig_count = get_count(
            con,
            f"""
            SELECT COUNT(*)
            FROM read_parquet('{input_path}')
            """,
        )

        print(f"Total de registros na origem: {orig_count:,}")

        # ====================================================
        # 2. EXECUTAR PARTICIONAMENTO
        # ====================================================

        print("\nExecutando COPY ... PARTITION_BY (uf)...")

        query = f"""
            COPY (
                SELECT *
                FROM read_parquet('{input_path}')
            )
            TO '{output_path}'
            (
                FORMAT PARQUET,
                PARTITION_BY (uf),
                COMPRESSION 'SNAPPY'
            );
        """

        con.execute(query)

        print("Particionamento executado.")

        # ====================================================
        # 3. VERIFICAR ARQUIVOS DE SAÍDA
        # ====================================================

        output_files = list(OUTPUT_DIR.rglob("*.parquet"))

        if not output_files:
            raise RuntimeError(
                "Nenhum arquivo Parquet foi criado no diretório de saída."
            )

        print(f"Arquivos Parquet gerados: {len(output_files)}")

        # ====================================================
        # 4. CONTAGEM DO DESTINO
        # ====================================================

        print("\n--- CONTAGEM DO DESTINO ---")

        dest_path = str(OUTPUT_DIR / "**" / "*.parquet").replace("\\", "/")

        dest_count = get_count(
            con,
            f"""
            SELECT COUNT(*)
            FROM read_parquet(
                '{dest_path}',
                hive_partitioning = true
            )
            """,
        )

        print(f"Total de registros no destino: {dest_count:,}")

        # ====================================================
        # 5. COMPARAR ORIGEM E DESTINO
        # ====================================================

        diff = orig_count - dest_count

        print(f"Diferença (Origem - Destino): {diff:,}")

        if diff == 0:
            print("OK: quantidade de registros preservada.")
        else:
            print("ERRO: quantidade de registros não confere.")

        # ====================================================
        # 6. CONTAGEM POR UF
        # ====================================================

        print("\n--- CONTAGEM POR UF (DESTINO) ---")

        df_ufs = con.execute(
            f"""
            SELECT
                uf,
                COUNT(*) AS qtd

            FROM read_parquet(
                '{dest_path}',
                hive_partitioning = true
            )

            GROUP BY uf

            ORDER BY qtd DESC
            """
        ).df()

        print(df_ufs.to_string(index=False))

        # ====================================================
        # 7. VALIDAÇÃO DA UF BA
        # ====================================================

        print("\n--- VALIDAÇÃO UF 'BA' ---")

        orig_ba = get_count(
            con,
            f"""
            SELECT COUNT(*)
            FROM read_parquet('{input_path}')
            WHERE uf = 'BA'
            """,
        )

        dest_ba_path = str(OUTPUT_DIR / "uf=BA" / "*.parquet").replace("\\", "/")

        ba_files = list((OUTPUT_DIR / "uf=BA").glob("*.parquet"))

        if not ba_files:
            raise RuntimeError("A partição uf=BA não foi encontrada.")

        dest_ba = get_count(
            con,
            f"""
            SELECT COUNT(*)
            FROM read_parquet('{dest_ba_path}')
            """,
        )

        print(f"Origem BA : {orig_ba:,}")

        print(f"Destino BA: {dest_ba:,}")

        print(f"Match BA  : {orig_ba == dest_ba}")

        if orig_ba != dest_ba:
            print("ERRO: quantidade de registros da BA não confere.")

        # ====================================================
        # 8. SCHEMA
        # ====================================================

        print("\n--- SCHEMA DA PARTIÇÃO ---")

        sample_parquet = output_files[0]

        desc = con.execute(
            f"""
            DESCRIBE
            SELECT *
            FROM read_parquet(
                '{sample_parquet.as_posix()}'
            )
            """
        ).df()

        print(desc[["column_name", "column_type"]].to_string(index=False))

        # ====================================================
        # 9. RESULTADO FINAL
        # ====================================================

        print("\n" + "=" * 70)

        if diff == 0 and orig_ba == dest_ba:
            print("PARTICIONAMENTO CONCLUÍDO COM SUCESSO!")

        else:
            print("PARTICIONAMENTO CONCLUÍDO, MAS HÁ FALHAS DE VALIDAÇÃO.")

        print("=" * 70)

    finally:
        con.close()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    run_partitioning()

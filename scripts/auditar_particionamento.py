from pathlib import Path

import duckdb

# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(r"C:\Users\victo\Desktop\BUSCACNPJ")

INPUT_DIR = BASE_DIR / "data" / "processed_corrigido" / "estabelecimentos"

OUTPUT_DIR = BASE_DIR / "data" / "particionado" / "estabelecimentos"


# ============================================================
# FUNÇÃO AUXILIAR PARA CONSULTAS ESCALARES
# ============================================================


def scalar(con, query):
    """
    Executa uma consulta que deve retornar uma única linha
    e devolve o primeiro campo.

    Evita:
        Object of type "None" is not subscriptable
    """

    result = con.execute(query).fetchone()

    if result is None:
        raise RuntimeError("A consulta não retornou nenhum resultado.")

    return result[0]


# ============================================================
# AUDITORIA
# ============================================================


def run_audit():

    print("Iniciando auditoria de integridade do particionamento...")

    # --------------------------------------------------------
    # Verificar diretórios
    # --------------------------------------------------------

    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Diretório de entrada não encontrado:\n{INPUT_DIR}")

    if not OUTPUT_DIR.exists():
        raise FileNotFoundError(f"Diretório de destino não encontrado:\n{OUTPUT_DIR}")

    # --------------------------------------------------------
    # Verificar arquivos
    # --------------------------------------------------------

    input_files = list(INPUT_DIR.glob("*.parquet"))

    dest_files = list(OUTPUT_DIR.rglob("*.parquet"))

    if not input_files:
        raise FileNotFoundError(f"Nenhum Parquet encontrado em:\n{INPUT_DIR}")

    if not dest_files:
        raise FileNotFoundError(f"Nenhum Parquet encontrado em:\n{OUTPUT_DIR}")

    # --------------------------------------------------------
    # Caminhos DuckDB
    # --------------------------------------------------------

    input_path = str(INPUT_DIR / "*.parquet").replace("\\", "/")

    dest_path = str(OUTPUT_DIR / "**" / "*.parquet").replace("\\", "/")

    # --------------------------------------------------------
    # Conexão
    # --------------------------------------------------------

    con = duckdb.connect()

    try:
        # ====================================================
        # 1. QUANTIDADE TOTAL DE REGISTROS
        # ====================================================

        print("\nVerificando contagem total...")

        orig_count = scalar(
            con,
            f"""
            SELECT COUNT(*)
            FROM read_parquet('{input_path}')
            """,
        )

        dest_count = scalar(
            con,
            f"""
            SELECT COUNT(*)
            FROM read_parquet(
                '{dest_path}',
                hive_partitioning = true
            )
            """,
        )

        diff = orig_count - dest_count

        # ====================================================
        # 2. UFs ENCONTRADAS
        # ====================================================

        print("Verificando UFs e nulos...")

        orig_ufs_df = con.execute(
            f"""
            SELECT DISTINCT uf
            FROM read_parquet('{input_path}')
            ORDER BY uf
            """
        ).df()

        orig_ufs = orig_ufs_df["uf"].tolist()

        dest_ufs_df = con.execute(
            f"""
            SELECT DISTINCT uf
            FROM read_parquet(
                '{dest_path}',
                hive_partitioning = true
            )
            ORDER BY uf
            """
        ).df()

        dest_ufs = dest_ufs_df["uf"].tolist()

        # ====================================================
        # 3. UFs NULAS OU VAZIAS
        # ====================================================

        orig_null_uf = scalar(
            con,
            f"""
            SELECT COUNT(*)
            FROM read_parquet('{input_path}')
            WHERE uf IS NULL
               OR TRIM(uf) = ''
            """,
        )

        dest_null_uf = scalar(
            con,
            f"""
            SELECT COUNT(*)
            FROM read_parquet(
                '{dest_path}',
                hive_partitioning = true
            )
            WHERE uf IS NULL
               OR TRIM(uf) = ''
            """,
        )

        # ====================================================
        # 4. ISOLAMENTO DAS PARTIÇÕES
        # ====================================================

        print("Verificando isolamento das partições...")

        partition_violations = 0

        for uf_val in dest_ufs:
            if uf_val is None or str(uf_val).strip() == "":
                continue

            uf = str(uf_val).strip()

            part_file_path = str(OUTPUT_DIR / f"uf={uf}" / "*.parquet").replace(
                "\\", "/"
            )

            viol = scalar(
                con,
                f"""
                SELECT COUNT(*)
                FROM read_parquet(
                    '{part_file_path}'
                )
                WHERE uf != '{uf}'
                """,
            )

            if viol > 0:
                partition_violations += viol

        # ====================================================
        # 5. CNPJs DISTINTOS
        # ====================================================

        print("Verificando CNPJs distintos...")

        orig_cnpjs = scalar(
            con,
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv
                FROM read_parquet('{input_path}')
            )
            """,
        )

        dest_cnpjs = scalar(
            con,
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv
                FROM read_parquet(
                    '{dest_path}',
                    hive_partitioning = true
                )
            )
            """,
        )

        # ====================================================
        # 6. CHAVES SOMENTE NA ORIGEM
        # ====================================================

        print("Verificando chaves exclusivas...")

        only_in_orig = scalar(
            con,
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv
                FROM read_parquet('{input_path}')

                EXCEPT

                SELECT DISTINCT
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv
                FROM read_parquet(
                    '{dest_path}',
                    hive_partitioning = true
                )
            )
            """,
        )

        # ====================================================
        # 7. CHAVES SOMENTE NO DESTINO
        # ====================================================

        only_in_dest = scalar(
            con,
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv
                FROM read_parquet(
                    '{dest_path}',
                    hive_partitioning = true
                )

                EXCEPT

                SELECT DISTINCT
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv
                FROM read_parquet('{input_path}')
            )
            """,
        )

        # ====================================================
        # 8. DUPLICIDADES NA ORIGEM
        # ====================================================

        print("Verificando duplicidades...")

        orig_dupes = scalar(
            con,
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv,
                    COUNT(*) AS c

                FROM read_parquet('{input_path}')

                GROUP BY
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv

                HAVING COUNT(*) > 1
            )
            """,
        )

        # ====================================================
        # 9. DUPLICIDADES NO DESTINO
        # ====================================================

        dest_dupes = scalar(
            con,
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv,
                    COUNT(*) AS c

                FROM read_parquet(
                    '{dest_path}',
                    hive_partitioning = true
                )

                GROUP BY
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv

                HAVING COUNT(*) > 1
            )
            """,
        )

    finally:
        con.close()

    # ========================================================
    # RELATÓRIO FINAL
    # ========================================================

    print("\n" + "=" * 60)
    print("RELATÓRIO DE AUDITORIA DE PARTICIONAMENTO")
    print("=" * 60)

    print(f"Registros origem: {orig_count:,}")

    print(f"Registros destino: {dest_count:,}")

    print(f"Diferença de registros: {diff:,}")

    print(f"CNPJs distintos origem: {orig_cnpjs:,}")

    print(f"CNPJs distintos destino: {dest_cnpjs:,}")

    print(f"UFs encontradas origem: {orig_ufs}")

    print(f"UFs encontradas destino: {dest_ufs}")

    print(f"Registros UF nulos/vazios origem: {orig_null_uf}")

    print(f"Registros UF nulos/vazios destino: {dest_null_uf}")

    print(f"Violações de isolamento nas partições: {partition_violations}")

    print(f"Duplicidades de chave na origem: {orig_dupes:,}")

    print(f"Duplicidades de chave no destino: {dest_dupes:,}")

    print(f"Chaves somente na origem: {only_in_orig:,}")

    print(f"Chaves somente no destino: {only_in_dest:,}")

    # ========================================================
    # AVALIAÇÃO
    # ========================================================

    aprovado = (
        diff == 0
        and orig_cnpjs == dest_cnpjs
        and orig_ufs == dest_ufs
        and orig_null_uf == 0
        and dest_null_uf == 0
        and partition_violations == 0
        and orig_dupes == dest_dupes
        and only_in_orig == 0
        and only_in_dest == 0
    )

    print("=" * 60)

    if aprovado:
        print("CONCLUSÃO FINAL: APROVADO — integridade confirmada")

    else:
        print("CONCLUSÃO FINAL: REPROVADO — existem inconsistências")

    print("=" * 60)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    run_audit()

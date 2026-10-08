from pathlib import Path

import duckdb

# ============================================================
# CONFIGURAÇÕES
# ============================================================

INPUT_PARQUET = Path(r"data/processed/socios/Socios0.parquet")

OUTPUT_DIR = Path(r"data/prototipo")
OUTPUT_PARQUET = OUTPUT_DIR / "socios_corrigido.parquet"

SCHEMA_EXPECTED = [
    "cnpj_basico",
    "identificador_socio",
    "nome_socio",
    "cnpj_cpf_socio",
    "qualificacao_socio",
    "data_entrada_sociedade",
    "pais",
    "representante_legal",
    "nome_representante",
    "qualificacao_representante",
    "faixa_etaria",
]


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================


def run_prototipo():

    print("=" * 70)
    print("PROTÓTIPO - CORREÇÃO DO PARQUET")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Verificar arquivo de entrada
    # --------------------------------------------------------

    if not INPUT_PARQUET.exists():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado:\n{INPUT_PARQUET.resolve()}"
        )

    print("\nArquivo de entrada:")
    print(f"  {INPUT_PARQUET.resolve()}")

    # --------------------------------------------------------
    # 2. Criar diretório de saída
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nDiretório de saída:")
    print(f"  {OUTPUT_DIR.resolve()}")

    # --------------------------------------------------------
    # 3. Abrir DuckDB
    # --------------------------------------------------------

    with duckdb.connect() as con:
        # ----------------------------------------------------
        # 4. Inspecionar o schema original
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("1. SCHEMA ORIGINAL")
        print("-" * 70)

        describe_query = f"""
            DESCRIBE
            SELECT *
            FROM read_parquet('{INPUT_PARQUET.as_posix()}')
        """

        schema_df = con.execute(describe_query).df()

        print(schema_df.to_string(index=False))

        # ----------------------------------------------------
        # 5. Verificar quantidade de colunas
        # ----------------------------------------------------

        actual_columns = schema_df["column_name"].tolist()

        print("\nColunas encontradas:")
        print(actual_columns)

        expected_columns_original = [str(i) for i in range(len(SCHEMA_EXPECTED))]

        if actual_columns != expected_columns_original:
            raise ValueError(
                "\nSchema inesperado!\n"
                f"Esperado: {expected_columns_original}\n"
                f"Encontrado: {actual_columns}"
            )

        print("\nOK: foram encontradas as 11 colunas esperadas.")

        # ----------------------------------------------------
        # 6. Ler primeira linha
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("2. VERIFICANDO CABEÇALHO")
        print("-" * 70)

        header_query = f"""
            SELECT *
            FROM read_parquet('{INPUT_PARQUET.as_posix()}')
            LIMIT 1
        """

        header = con.execute(header_query).fetchone()

        if header is None:
            raise ValueError("O arquivo Parquet está vazio.")

        print("\nPrimeira linha encontrada:")

        for i, value in enumerate(header):
            print(f"  [{i}] {value!r}")

        # ----------------------------------------------------
        # 7. Validar cabeçalho completo
        # ----------------------------------------------------

        header_as_text = [
            str(value).strip() if value is not None else "" for value in header
        ]

        print("\nCabeçalho detectado:")
        print(header_as_text)

        if header_as_text != SCHEMA_EXPECTED:
            print("\nERRO: o cabeçalho encontrado não corresponde ao esperado.")

            print("\nEsperado:")
            print(SCHEMA_EXPECTED)

            print("\nEncontrado:")
            print(header_as_text)

            raise ValueError(
                "O cabeçalho do arquivo não corresponde ao SCHEMA_EXPECTED."
            )

        print("\nOK: cabeçalho validado com sucesso.")

        # ----------------------------------------------------
        # 8. Contagem original
        # ----------------------------------------------------

        result = con.execute(
            f"""
            SELECT COUNT(*)
            FROM read_parquet('{INPUT_PARQUET.as_posix()}')
            """
        ).fetchone()

        if result is None:
            raise RuntimeError(
                "Não foi possível obter a quantidade de linhas do arquivo original."
            )

        orig_count = result[0]

        print(f"\nQuantidade original de linhas: {orig_count}")

        # ----------------------------------------------------
        # 9. Montar SELECT de transformação
        # ----------------------------------------------------

        select_cols = []

        for i, name in enumerate(SCHEMA_EXPECTED):
            select_cols.append(f'CAST("{i}" AS VARCHAR) AS "{name}"')

        select_sql = ",\n                ".join(select_cols)

        # ----------------------------------------------------
        # 10. Criar Parquet corrigido
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("3. CRIANDO PARQUET CORRIGIDO")
        print("-" * 70)

        query = f"""
            COPY (
                SELECT
                    {select_sql}

                FROM read_parquet('{INPUT_PARQUET.as_posix()}')

                WHERE CAST("0" AS VARCHAR) <> 'cnpj_basico'
            )

            TO '{OUTPUT_PARQUET.as_posix()}'

            (
                FORMAT PARQUET,
                OVERWRITE_OR_IGNORE TRUE
            );
        """

        print("\nExecutando transformação...")

        con.execute(query)

        print("Transformação concluída.")

        # ----------------------------------------------------
        # 11. Validar arquivo gerado
        # ----------------------------------------------------

        if not OUTPUT_PARQUET.exists():
            raise RuntimeError("O arquivo de saída não foi criado.")

        result = con.execute(
            f"""
                SELECT COUNT(*) AS total
                FROM read_parquet('{OUTPUT_PARQUET.as_posix()}')
                """
        ).fetchone()

        if result is None:
            raise RuntimeError(
                "O DuckDB não retornou resultado ao consultar o arquivo de saída."
            )

        new_count = result[0]

        print("\n" + "-" * 70)
        print("4. VALIDAÇÃO")
        print("-" * 70)

        print(f"\nLinhas antes : {orig_count}")
        print(f"Linhas depois: {new_count}")

        removed_header = orig_count - new_count

        print(f"Linhas removidas: {removed_header}")

        if removed_header == 1:
            print("OK: exatamente uma linha de cabeçalho foi removida.")

        elif removed_header == 0:
            print("ATENÇÃO: nenhuma linha foi removida.")

        else:
            print("ATENÇÃO: quantidade inesperada de linhas removidas.")

        # ----------------------------------------------------
        # 12. Validar schema final
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("5. SCHEMA FINAL")
        print("-" * 70)

        final_schema = con.execute(
            f"""
            DESCRIBE
            SELECT *
            FROM read_parquet('{OUTPUT_PARQUET.as_posix()}')
            """
        ).df()

        print(final_schema.to_string(index=False))

        final_columns = final_schema["column_name"].tolist()

        if final_columns == SCHEMA_EXPECTED:
            print("\nOK: nomes das colunas estão corretos.")

        else:
            print("\nERRO: nomes das colunas estão incorretos.")

            print("Esperado:")
            print(SCHEMA_EXPECTED)

            print("Encontrado:")
            print(final_columns)

        # ----------------------------------------------------
        # 13. Mostrar primeiros registros
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("6. PRIMEIROS 3 REGISTROS")
        print("-" * 70)

        first_rows = con.execute(
            f"""
            SELECT *
            FROM read_parquet('{OUTPUT_PARQUET.as_posix()}')
            LIMIT 3
            """
        ).df()

        print(first_rows.to_string(index=False))

        # ----------------------------------------------------
        # 14. Resumo
        # ----------------------------------------------------

        print("\n" + "=" * 70)
        print("PROTÓTIPO FINALIZADO")
        print("=" * 70)

        print("\nArquivo gerado:")
        print(f"  {OUTPUT_PARQUET.resolve()}")

        print(f"\nLinhas originais : {orig_count}")
        print(f"Linhas corrigidas: {new_count}")

        print("\nStatus: OK")


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    run_prototipo()

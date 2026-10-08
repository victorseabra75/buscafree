import json
import shutil
import sys
from pathlib import Path

import duckdb

# Configurações
BASE_DIR = Path(r"C:\Users\victo\Desktop\BUSCACNPJ")
INPUT_BASE_DIR = BASE_DIR / "data" / "processed"
OUTPUT_BASE_DIR = BASE_DIR / "data" / "processed_corrigido"
SCHEMA_DIR = BASE_DIR / "data" / "schema"


def get_schema_for_table(table_name):
    schema_file = SCHEMA_DIR / f"{table_name}.json"
    if not schema_file.exists():
        return None
    with open(schema_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return list(data["columns"].keys())


def validate_space(input_size_bytes):
    _, _, free = shutil.disk_usage(BASE_DIR)
    return free


def run_correction():
    files = list(INPUT_BASE_DIR.rglob("*.parquet"))
    total_size = sum(f.stat().st_size for f in files)

    if validate_space(total_size) < total_size * 1.1:
        print("Erro: Espaço insuficiente em disco.")
        sys.exit(1)

    results = []
    has_errors = False
    con = duckdb.connect()

    for file_path in files:
        table_name = file_path.parent.name
        schema_expected = get_schema_for_table(table_name)

        if not schema_expected:
            print(f"Erro: Schema não encontrado para {table_name}")
            has_errors = True
            continue

        output_path = OUTPUT_BASE_DIR / table_name / file_path.name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 1. Validar primeira linha
            first_row = con.execute(f"SELECT * FROM '{file_path}' LIMIT 1").fetchone()
            if first_row != tuple(schema_expected):
                print(f"Erro: Cabeçalho inválido em {file_path}")
                has_errors = True
                continue

            # 2. Processar
            select_cols = [
                f'"{i}" AS "{name}"' for i, name in enumerate(schema_expected)
            ]
            query = f"""
                COPY (
                    SELECT {", ".join(select_cols)}
                    FROM '{file_path}'
                    WHERE "{0}" != '{schema_expected[0]}'
                ) TO '{output_path}' (FORMAT 'PARQUET');
            """
            con.execute(query)

            # 3. Validações Pós-Gravação

            orig_result = con.execute(f"SELECT COUNT(*) FROM '{file_path}'").fetchone()

            if orig_result is None:
                raise RuntimeError(
                    f"Não foi possível obter a contagem do arquivo original: {file_path}"
                )

            orig_count = orig_result[0]

            new_result = con.execute(f"SELECT COUNT(*) FROM '{output_path}'").fetchone()

            if new_result is None:
                raise RuntimeError(
                    f"Não foi possível obter a contagem do arquivo corrigido: {output_path}"
                )

            new_count = new_result[0]

            diff = orig_count - new_count

            desc = con.execute(f"DESCRIBE SELECT * FROM '{output_path}'").df()
            schema_valid = list(desc["column_name"]) == schema_expected

            if diff != 1 or not schema_valid:
                print(
                    f"Erro de validação em {file_path}: diff={diff}, schema_valid={schema_valid}"
                )
                has_errors = True
                continue

            results.append(
                {
                    "table": table_name,
                    "file": file_path.name,
                    "orig": orig_count,
                    "new": new_count,
                    "diff": diff,
                    "schema": schema_valid,
                    "status": "OK",
                }
            )
            print(f"OK: {file_path.name}")

        except duckdb.Error as e:
            print(f"Falha crítica em {file_path}: {e}")
            has_errors = True

    con.close()

    # Relatório Final
    print("\n--- RELATÓRIO ---")
    for r in results:
        print(
            f"{r['table']} | {r['file']} | {r['orig']} -> {r['new']} | Diff:{r['diff']} | Schema: {r['schema']}"
        )

    total_files = len(files)
    success = len(results)
    print(
        f"\nArquivos: {total_files} | Sucesso: {success} | Erro: {total_files - success}"
    )

    if has_errors or (sum(r["diff"] for r in results) != success):
        print("Erro: Validação global falhou.")
        sys.exit(1)


if __name__ == "__main__":
    run_correction()

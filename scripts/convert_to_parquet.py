import os  # noqa: F401
import shutil
import subprocess
from pathlib import Path

import duckdb
import pandas as pd

# Configurações
BASE_DIR = Path(r"C:\Users\victo\Desktop\BUSCACNPJ")
RAW_DIR = BASE_DIR / "data" / "preprocessed"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
R2_REMOTE = "r2:buscafri-data"


def get_rclone_path():
    path = shutil.which("rclone")
    if not path:
        path = r"C:\Users\victo\Desktop\BUSCACNPJ\rclone.exe"
    return path


def get_table_name(file_name):
    name = file_name.upper()
    if "CNAE" in name: 
        return "cnaes"
    if "EMPRE" in name: 
        return "empresas"
    if "ESTAB" in name: 
        return "estabelecimentos"
    if "MOTI" in name: 
        return "motivos"
    if "MUNIC" in name: 
        return "municipios"
    if "NATJU" in name: 
        return "naturezas"
    if "PAIS" in name: 
        return "paises"
    if "QUAL" in name: 
        return "qualificacoes"
    if "SIMPLE" in name: 
        return "simples"
    if "SOCIO" in name: 
        return "socios"
    return Path(file_name).stem



def convert_to_parquet(file_path):
    rclone_bin = get_rclone_path()
    table_name = get_table_name(file_path.name)
    parquet_filename = f"{file_path.stem}.parquet"

    # Caminhos
    local_table_dir = PROCESSED_DIR / table_name
    local_table_dir.mkdir(parents=True, exist_ok=True)
    output_parquet = local_table_dir / parquet_filename
    r2_destination = f"{R2_REMOTE}/{table_name}"

    print(f"\n🔄 Analisando: {file_path.name}")

    # 1. VERIFICAÇÃO LOCAL
    if output_parquet.exists():
        print(f"   ⏩ {parquet_filename} já existe localmente.")
    else:
        print("   ⚙️ Convertendo (Chunking)...")
        try:
            con = duckdb.connect()
            chunk_size = 100000
            first_chunk = True

            for chunk in pd.read_csv(
                file_path,
                sep=";",
                encoding="ISO-8859-1",
                header=None,
                dtype=str,
                chunksize=chunk_size,
            ):
                con.register("df_chunk", chunk)
                if first_chunk:
                    con.execute("CREATE TABLE temp_table AS SELECT * FROM df_chunk")
                    first_chunk = False
                else:
                    con.execute("INSERT INTO temp_table SELECT * FROM df_chunk")

            con.execute(
                f"COPY temp_table TO '{str(output_parquet).replace(chr(92), '/')}' (FORMAT 'PARQUET', COMPRESSION 'SNAPPY');"
            )
            con.close()
            print(f"   ✅ Conversão local concluída: {parquet_filename}")
        except duckdb.Error as e:
            print(f"   ❌ Erro na conversão: {e}")
            return

    # 2. VERIFICAÇÃO R2 (LSL)
    # Lista arquivos no bucket específico da tabela
    check_r2 = subprocess.run(
        [rclone_bin, "lsl", f"{r2_destination}"],
        capture_output=True,
        text=True,
        check=False,
    )

    if parquet_filename in check_r2.stdout:
        print(f"   ⏩ {parquet_filename} já está no R2. Pulando upload.")
    else:
        print(f"   ☁️ Subindo para {r2_destination}...")
        subprocess.run(
            [rclone_bin, "copy", str(output_parquet), r2_destination], check=False
        )
        print("   🚀 Upload finalizado!")


def run_pipeline():
    files = [
        f for f in RAW_DIR.rglob("*") if f.is_file() and not f.name.startswith(".")
    ]
    if not files:
        print("⚠️ Nenhum arquivo encontrado.")
        return

    for file_path in files:
        convert_to_parquet(file_path)

    print("\n🚀 Todos os arquivos foram processados!")


if __name__ == "__main__":
    run_pipeline()

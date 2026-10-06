import os

import duckdb
from dotenv import load_dotenv

load_dotenv()

R2_MOUNT_PATH = os.getenv("R2_MOUNT_PATH", "/mnt/data/buscafri")


class DuckDBClient:
    def __init__(self):
        self.conn: duckdb.DuckDBPyConnection | None = None
        self.connect()

    def connect(self):
        try:
            self.conn = duckdb.connect(
                database=":memory:",
                read_only=False,
            )

            print("✅ Conectado ao DuckDB")

        except Exception as e:  # noqa: BLE001
            self.conn = None
            print(f"❌ Erro ao conectar ao DuckDB: {e}")

    def query(self, sql):
        if self.conn is None:
            self.connect()

        if self.conn is None:
            raise RuntimeError("Não foi possível conectar ao DuckDB.")

        return self.conn.execute(sql).df()


db_client = DuckDBClient()
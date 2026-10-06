import os

import duckdb
from dotenv import load_dotenv

load_dotenv()

# Configurações do R2 para DuckDB
# Em produção, o DuckDB pode usar o rclone mount ou acessar via httpfs
# Para hobbista, usar o caminho do rclone mount é o mais estável na e2-micro
R2_MOUNT_PATH = os.getenv("R2_MOUNT_PATH", "/mnt/data/buscafri")


class DuckDBClient:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            # Conecta em modo read_only para evitar locks durante consultas da API
            self.conn = duckdb.connect(database=":memory:", read_only=False)

            # Se estiver usando httpfs, as chaves precisam estar aqui:
            # self.conn.execute("INSTALL httpfs; LOAD httpfs;")
            # self.conn.execute(f"SET s3_endpoint='{os.getenv('R2_ENDPOINT')}';")
            # self.conn.execute(f"SET s3_access_key_id='{os.getenv('R2_ACCESS_KEY_ID')}';")
            # self.conn.execute(f"SET s3_secret_access_key='{os.getenv('R2_SECRET_ACCESS_KEY')}';")
            # self.conn.execute("SET s3_region='auto';")

            print("✅ Conectado ao DuckDB")
        except Exception as e:
            print(f"❌ Erro ao conectar ao DuckDB: {e}")

    def query(self, sql):
        if not self.conn:
            self.connect()
        return self.conn.execute(sql).df()


db_client = DuckDBClient()

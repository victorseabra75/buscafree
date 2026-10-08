import os
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Configurações do R2 obtidas do .env ou padrão
R2_REMOTE = os.getenv("R2_REMOTE", "r2:buscafri-data")
CHECK_INTERVAL = 5  # segundos


def get_rclone_path():
    local_rclone = Path("rclone.exe")

    if local_rclone.exists():
        return str(local_rclone.absolute())

    return "rclone"


def check_connectivity():
    rclone_bin = get_rclone_path()

    access_key = os.getenv("R2_ACCESS_KEY_ID")
    if not access_key:
        raise ValueError("A variável de ambiente R2_ACCESS_KEY_ID não está definida.")

    secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    if not secret_key:
        raise ValueError(
            "A variável de ambiente R2_SECRET_ACCESS_KEY não está definida."
        )

    endpoint = os.getenv("R2_ENDPOINT")
    if not endpoint:
        raise ValueError("A variável de ambiente R2_ENDPOINT não está definida.")

    print(f"🔍 Iniciando monitoramento de conectividade com {R2_REMOTE}...")

    try:
        while True:
            start_time = time.time()

            # Passa as variáveis de ambiente do .env para o subprocesso do rclone.
            env = os.environ.copy()

            access_key = os.getenv("R2_ACCESS_KEY_ID")
            secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
            endpoint = os.getenv("R2_ENDPOINT")

            if access_key:
                env["RCLONE_R2_ACCESS_KEY_ID"] = access_key

            if secret_key:
                env["RCLONE_R2_SECRET_ACCESS_KEY"] = secret_key

            if endpoint:
                env["RCLONE_R2_ENDPOINT"] = endpoint

            result = subprocess.run(
                [rclone_bin, "lsf", R2_REMOTE, "--max-depth", "1"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                env=env,
            )

            latency = (time.time() - start_time) * 1000

            if result.returncode == 0:
                sys.stdout.write(
                    f"\r✅ R2 Online | Latência: {latency:.2f}ms | Status: OK   "
                )
            else:
                err_msg = result.stderr.strip().replace("\n", " ")

                sys.stdout.write(f"\r❌ R2 Falhou | Erro: {err_msg[:45]}...          ")

            sys.stdout.flush()
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Monitoramento encerrado pelo usuário.")

    except Exception as e:  # noqa: BLE001
        print(f"\n❌ Erro crítico no monitor: {e}")


if __name__ == "__main__":
    check_connectivity()

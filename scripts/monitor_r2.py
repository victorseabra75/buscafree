import subprocess
import sys
import time
from pathlib import Path

# Configurações
R2_REMOTE = "r2:buscafri-data"
CHECK_INTERVAL = 5  # segundos


def get_rclone_path():
    # Tenta local primeiro, depois PATH
    local_rclone = Path("rclone.exe")
    if local_rclone.exists():
        return str(local_rclone.absolute())
    return "rclone"


def check_connectivity():
    rclone_bin = get_rclone_path()
    print(f"🔍 Iniciando monitoramento de conectividade com {R2_REMOTE}...")

    try:
        while True:
            start_time = time.time()

            # Executa um comando leve para testar a conexão (lsf limitado a 1 item)
            result = subprocess.run(
                [rclone_bin, "lsf", R2_REMOTE, "--max-depth", "1"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            latency = (time.time() - start_time) * 1000

            if result.returncode == 0:
                sys.stdout.write(
                    f"\r✅ R2 Online | Latência: {latency:.2f}ms | Status: OK   "
                )
            else:
                sys.stdout.write(
                    f"\r❌ R2 Falhou | Erro: {result.stderr[:30]}...          "
                )

            sys.stdout.flush()
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Monitoramento encerrado pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro crítico no monitor: {e}")


if __name__ == "__main__":
    check_connectivity()

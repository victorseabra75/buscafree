#!/bin/bash
# Script de Setup Final: BuscaFri
set -e

echo "🚀 Iniciando Setup Completo..."

# 1. Instala pacotes básicos
sudo apt update && sudo apt install -y python3-pip python3-venv git fuse3 nano tmux
sudo -v ; curl https://rclone.org/install.sh | sudo bash

# 2. Configura ambiente Python (UV)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# 3. Setup do diretório e Alias
cd $HOME
git clone https://github.com/victorseabra75/buscafree.git
cd buscafree
uv venv buscafree
source buscafree/bin/activate
uv pip install -r requirements.txt

# 4. Alias go-busca
echo 'alias go-busca="cd ~/buscafree && source buscafree/bin/activate"' >> ~/.bashrc
source ~/.bashrc

# 5. Rclone (Copia a config que você deve colocar no repo)
mkdir -p $HOME/.config/rclone/
cp rclone.conf $HOME/.config/rclone/rclone.conf

# 6. Systemd (API)
cat <<EOF | sudo tee /etc/systemd/system/buscafri-api.service
[Unit]
Description=BuscaFri API
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/buscafree
Environment="PATH=$HOME/buscafree/buscafree/bin:\$PATH"
ExecStart=$HOME/buscafree/buscafree/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 7. Systemd (Streamlit UI - Exemplo)
cat <<EOF | sudo tee /etc/systemd/system/buscafri-ui.service
[Unit]
Description=BuscaFri Dashboard
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/buscafree
Environment="PATH=$HOME/buscafree/buscafree/bin:\$PATH"
ExecStart=$HOME/buscafree/buscafree/bin/streamlit run scripts/ui.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 8. Start dos serviços
sudo systemctl daemon-reload
sudo systemctl enable buscafri-api buscafri-ui
sudo systemctl restart buscafri-api buscafri-ui

echo "✅ Setup finalizado! API na 8000, UI na 8501."
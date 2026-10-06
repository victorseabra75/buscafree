#!/bin/bash
# Script de Setup Final: BuscaFri (Atualizado e Otimizado)
set -e

echo "🚀 Iniciando Setup Completo do BuscaFri..."

# 1. Instala pacotes básicos
sudo apt update && sudo apt install -y python3-pip python3-venv git fuse3 nano tmux curl -y

# 2. Instala o UV (Gerenciador Python ultrarrápido)
if ! command -v uv &> /dev/null; then
    echo "📦 Instalando uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
fi

# 3. Setup do diretório do projeto
cd $HOME
if [ -d "buscafri" ]; then
    echo "📁 Pasta buscafri já existe. Atualizando repositório..."
    cd buscafri
    git pull origin main
else
    echo "📥 Clonando repositório..."
    git clone https://github.com/victorseabra75/buscafri.git
    cd buscafri
fi

# 4. Configura ambiente virtual e dependências com o uv
echo "🐍 Configurando venv e dependências..."
uv venv
uv sync

# 5. Cria o comando atalho 'go-busca' definitivo no ~/.local/bin
mkdir -p $HOME/.local/bin
cat << 'EOF' > $HOME/.local/bin/go-busca
#!/bin/bash
echo "🚀 Iniciando atualização do BuscaFri..."
cd ~/buscafri || { echo "❌ Pasta buscafri não encontrada!"; exit 1; }
echo "📥 Puxando últimas alterações do GitHub..."
git pull origin main
echo "📦 Sincronizando dependências..."
uv sync
echo "🔄 Reiniciando serviços (API e Streamlit)..."
sudo systemctl restart buscafri-api
sudo systemctl restart buscafri-streamlit
echo "✨ Deploy concluído com sucesso!"
sudo systemctl status buscafri-api buscafri-streamlit --no-pager
EOF
chmod +x $HOME/.local/bin/go-busca

# Garante que o PATH inclui o ~/.local/bin
if ! grep -q '.local/bin' ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi
source ~/.bashrc

# 6. Systemd (API FastAPI na porta 8000)
echo "⚙️ Configurando serviço systemd para a API FastAPI..."
sudo bash -c 'cat > /etc/systemd/system/buscafri-api.service' <<EOF
[Unit]
Description=BuscaFri FastAPI Application
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/buscafri
ExecStart=$HOME/.local/bin/uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 7. Systemd (Streamlit UI na porta 8501)
echo "⚙️ Configurando serviço systemd para o Streamlit..."
sudo bash -c 'cat > /etc/systemd/system/buscafri-streamlit.service' <<EOF
[Unit]
Description=BuscaFri Streamlit Frontend
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/buscafri
ExecStart=$HOME/.local/bin/uv run streamlit run app/ui.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 8. Ativa e inicia os serviços no Systemd
echo "🔄 Ativando serviços no systemd..."
sudo systemctl daemon-reload
sudo systemctl enable --now buscafri-api
sudo systemctl enable --now buscafri-streamlit

echo "✅ Setup finalizado com sucesso! API online na porta 8000 e Streamlit na 8501."
echo "💡 A partir de agora, para atualizar tudo na VPS após um git push, basta digitar: go-busca"
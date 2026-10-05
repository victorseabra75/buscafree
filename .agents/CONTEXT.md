# BuscaFri — Registro de Decisões Arquiteturais (ADR)

## 1. Visão Geral do Sistema
- **Objetivo**: API de consulta rápida a dados públicos CNPJ (Receita Federal).
- **Stack**: Python 3.14, FastAPI, DuckDB, Streamlit, Cloudflare R2, Rclone.
- **Ambiente**: VPS GCP e2-micro (1GB RAM) + Máquina Local (Windows).

## 2. Decisões de Arquitetura (ADR)
- **Bare Metal vs Docker**: Optado por **Bare Metal** (Python puro no Linux) para maximizar eficiência de 1GB de RAM.
- **Gerenciamento de Pacotes**: Uso de **UV** (Astral) em ambos ambientes para alta performance e estabilidade.
- **Armazenamento de Dados**: 
  - **Storage**: Cloudflare R2 (S3-compatible).
  - **Montagem**: `rclone` montando o bucket R2 no diretório `/mnt/data/buscafri` (ou equivalente local).
- **Pipeline de ETL**: 
  - **Entrada**: CSVs brutos (com inserção manual de cabeçalho via PowerShell).
  - **Processamento**: Streaming via DuckDB (evita estourar RAM).
  - **Formato**: Apache Parquet (Snappy) para performance.
- **Serviços**: Uso de `systemd` para garantir auto-restart da API e Dashboard (resiliência).

## 3. Fluxo de Dados (Data Flow)
1. **Download**: Arquivos CSV da Receita Federal salvos em `data/raw/`.
2. **Transformação**: Script `convert_to_parquet.py` lê CSV (com cabeçalhos) -> DuckDB (Streaming) -> Parquet.
3. **Upload**: Rclone sincroniza automaticamente os arquivos Parquet para o R2.
4. **Consulta**: API FastAPI consulta os arquivos Parquet diretamente do R2 (via `httpfs` do DuckDB).
5. **Dashboard**: Streamlit consome a API FastAPI (com Rate-limiting para evitar abuso).

## 4. Infraestrutura e Automação
- **Gerenciamento de Processos**: Serviços `systemd` (`buscafri-api.service`, `buscafri-ui.service`).
- **Ambiente Virtual**: Padronizado como `buscafree` via `uv`.
- **Acesso Externo**: Porta 8000 liberada no Firewall do GCP.
- **Porta**: A API responde em `http://35.190.151.11:8000/`.
- **Logs**: Monitoramento via `journalctl -u buscafri-api -f`.

## 5. Referências de Processamento
- **Mapeamento de Tabelas**: Documentado em `SPEC.md`.
- **Esquemas JSON**: Pasta `data/schema/*.json` (fonte de verdade para o ETL).
- **Manutenção Mensal**: 
  1. Inserir cabeçalhos nos CSVs (script `processar_receita.ps1`).
  2. Converter com `scripts/convert_to_parquet.py`.

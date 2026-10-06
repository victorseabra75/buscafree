# BuscaFri — Status do Projeto (PROJECT_STATUS.md)

## 1. Contexto & Arquitetura
**Objetivo do Projeto**: Plataforma (SaaS hobbista) focada em disponibilizar a base pública bruta de CNPJs da Receita Federal para consultas analíticas rápidas via API RESTful e interface visual de Dashboard.
**Hospedagem**: Google Cloud Platform (GCP) Compute Engine - VM `e2-micro` (1 vCPU, 1 GB RAM).

### Stack Tecnológico
- **Ingestão/ETL**: Python (Pandas + DuckDB) para processamento em streaming (chunking).
- **Armazenamento**: Cloudflare R2 (Object Storage S3-compatible).
- **Integração Cloud**: `rclone` (montagem de bucket como unidade local/sincronização).
- **Engine Analítica**: DuckDB (leitura eficiente de Parquets).
- **Backend (API)**: FastAPI com proteção de Rate-Limiting (`slowapi`).
- **Frontend (UI)**: Streamlit.
- **CI/CD e Qualidade**: GitHub Actions, `uv` (gerenciamento de ambiente), `ruff` (linter), `pytest`.

### Estrutura de Dados
- Formato **Apache Parquet** (compressão Snappy).
- Dados organizados no R2 em subpastas por domínio: `cnaes/`, `empresas/`, `estabelecimentos/`, `socios/`, etc.

---

## 2. Progresso Atual

### Infraestrutura e Setup
- [x] Configuração da VPS GCP (`e2-micro`).
- [x] Implementação de IaC via Terraform (`main.tf`).
- [x] Criação do script de Setup Automático Bare-Metal (`scripts/setup_vps.sh`) com `systemd` para auto-restart.
- [x] Padronização do ambiente Python com `uv` e ambiente virtual `buscafree`.

### ETL (Ingestão de Dados)
- [x] Script de extração web e download (`scripts/web_scraper.py`).
- [x] Mapeamento dos schemas das 10 tabelas da RFB (`data/schema/*.json`).
- [x] Script de Conversão CSV -> Parquet via DuckDB (`scripts/convert_to_parquet.py`).
- [x] Otimização contra `MemoryError` no ETL via leitura em `chunking` (blocos de 100k linhas) usando Pandas.
- [x] Redundância no R2: lógica para evitar uploads duplicados e manter backup local temporário.

### Backend (API FastAPI)
- [x] Endpoint Health-check (`/health`).
- [x] Endpoint de Busca Avançada (`GET /api/v1/busca`) com filtros de UF, Município, CNAE, Status, Email e Telefone.
- [x] Endpoint de Exportação via Streaming (`GET /api/v1/exportar/{formato}`) suportando CSV e XLSX.
- [x] Proteção e Segurança da API via Rate Limiting (10 req/min).

### CI/CD e Qualidade (QA)
- [x] Criação do Pipeline GitHub Actions (`.github/workflows/deploy.yml`).
- [x] Integração de injeção de segredos via SSH para deploy contínuo na VPS.
- [x] Criação da suíte de testes (`tests/`) para API e ETL.

### Frontend (Streamlit)
- [x] Desenvolvimento inicial da UI Dashboard (`app/ui.py`).
- [x] Implementação do processo em background (Threading) para manter o Rclone conectado ("Keep-Alive" no R2).
- [ ] Deploy do Streamlit e liberação da porta `8501`.

---

## 3. Decisões Técnicas & Otimizações (ADR)
1. **Bare Metal sobre Docker**: Abandonamos a ideia do Docker para o ambiente de produção a fim de preservar o limite restrito de 1GB de RAM da VM `e2-micro`.
2. **Separação Responsável no ETL**: O script de conversão não carrega grandes tabelas na RAM. Pandas é usado apenas para iterar o arquivo em *chunks* e passá-los ao DuckDB para escrita imediata no disco (geração do Parquet).
3. **Consulta Remota (httpfs vs rclone)**: Apesar de o DuckDB possuir extensão `httpfs`, optamos pelo uso contínuo do **Rclone** como ponte para o Cloudflare R2 por sua facilidade no upload durante o ETL. A API e a UI agora utilizam este espelhamento.
4. **Exportação Streaming**: As rotas de CSV/XLSX na API não geram arquivos físicos no servidor; utilizam o `StreamingResponse` com buffers em memória para não consumir espaço de disco.
5. **Automação de Deployment**: Toda a alteração na branch `main` executa `ruff`, valida os testes no `pytest` e entra via SSH na VPS apenas se o código estiver íntegro.

---

## 4. Próxima Task (A Fazer Agora na nova Janela)
**[TICKET-05] e [TICKET-06]: Refinamento do Streamlit e Validação Final**
- **Ação 1**: Confirmar se o deploy do GitHub Actions (commit recente) obteve êxito na VPS.
- **Ação 2**: Liberar a porta `8501` no Firewall da Google Cloud para acesso ao Dashboard.
- **Ação 3**: Testar exaustivamente a UI do Streamlit integrada à API (buscas e exportações).
- **Ação 4**: Monitorar os limites de RAM da VPS durante uma pesquisa pesada (ex: Filtro apenas por Estado "SP").

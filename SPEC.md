# 🛠️ BuscaFri — Especificação Técnica (SPEC)

**Versão:** 1.0  
**Status:** Em Construção

## 1. Arquitetura de Dados
### 1.1 Esquema de Arquivos (Raw to Processed)
- **Entrada:** Arquivos ZIP (ISO-8859-1, Separador `;`, Sem Header).
- **Processamento:** DuckDB streaming reader.
- **Saída:** Parquet (Snappy Compression).

### 1.2 Mapeamento de Tabelas (Principais)
#### Tabela: `Cnaes`
- `codigo` (INTEGER)
- `descricao` (VARCHAR)

#### Tabela: `Empresas`
- `cnpj_basico` (VARCHAR)
- `razao_social` (VARCHAR)
- `natureza_juridica` (VARCHAR)
- `qualificacao_responsavel` (VARCHAR)
- `capital_social` (DOUBLE)
- `porte_empresa` (VARCHAR)
- `ente_federativo_responsavel` (VARCHAR)

## 2. API Contracts (Endpoints)
### 2.1 `GET /api/v1/cnpj/{cnpj}`
- **Entrada:** String (14 dígitos).
- **Validação:** Pydantic (Regex p/ números).
- **Resposta:** JSON estruturado com dados de Empresa + Estabelecimento.

## 3. Infraestrutura & DevOps
### 3.1 Stack de Implantação
- **Host:** GCP e2-micro (Ubuntu 24.04 LTS).
- **Process Manager:** `uv` + `uvicorn` (inicialmente), `Gunicorn` (produção).
- **Storage:** Cloudflare R2 (S3 Compatible API).

### 3.2 CI/CD Pipeline
- **Trigger:** Push na branch `main`.
- **Action:** 
    1. SSH na VPS.
    2. `git pull`.
    3. `uv pip install -r requirements.txt`.
    4. Restart do serviço via `systemd`.

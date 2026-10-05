# 🏢 BuscaFri — API de Consulta & Analytics CNPJ

> **Domínio Oficial:** [buscafri.com.br](https://buscafri.com.br)  
> API RESTful e Motor de Analytics de alta performance projetada para ingestão, conversão em streaming e consulta analítica na base completa de dados abertos do CNPJ da Receita Federal do Brasil.

---

## 📄 PRD — Documento de Requisitos do Produto

**Versão:** 1.0  
**Status:** Em Desenvolvimento / Infraestrutura Pronta  
**Data da última atualização:** Março de 2024  
**Autor:** Victor Araújo Barros  

### 1. Visão Geral do Produto & Escopo
... (mantém o conteúdo) ...

---

### 2. Stack Tecnológico & Ferramental

| Componente | Tecnologia / Versão | Finalidade |
| :--- | :--- | :--- |
| **Gerenciador de Pacotes** | UV (Astral) | Gerenciamento de alta performance para ambiente e dependências. |
| **Ambiente Virtual** | `buscafree` | Ambiente padronizado Local e VPS. |
| **Documentação** | Swagger / OpenAPI | Auto-gerada via FastAPI em `/docs`. |
... (restante da tabela atualizado) ...

> ⚠️ **Requisito Crítico de Infraestrutura:**  
> Como a VM do GCP possui recursos limitados (1 vCPU e 1 GB RAM), é obrigatório não salvar a base inteira descompactada em disco. Utiliza-se o pipeline *"File-by-File" / Streaming*: processar **um arquivo ZIP por vez** (baixar $\rightarrow$ descompactar $\rightarrow$ converter em Parquet $\rightarrow$ subir para R2 $\rightarrow$ apagar arquivo local temporário).

---

### 2. Stack Tecnológico & Ferramental

| Componente | Tecnologia / Versão | Finalidade |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.12+ | Linguagem core para scripts de ETL e API. |
| **Web Framework** | FastAPI `>=0.115.6` & Uvicorn | Criação dos endpoints da API REST e documentação Swagger. |
| **Validação & Schemas** | Pydantic `>=2.10.4` | Schemas de dados e validação tipo strict (compatível com Python 3.13+). |
| **Engine Analítica** | DuckDB `>=1.1.0` | Processamento analítico em memória/disco com SQL de altíssima performance. |
| **Formato de Dados** | Apache Parquet / PyArrow | Formato colunar de alta compressão (snappy/zstd) e leitura rápida. |
| **Storage & Cloud** | Cloudflare R2 (`boto3`) | Armazenamento persistente dos arquivos Parquet (compatível com S3 sem custo de egress). |
| **Computação / VM** | GCP Compute Engine (`e2-micro`) | Hospedagem da API FastAPI e execução agendada do pipeline de ETL. |
| **Servidor Web / Proxy** | Nginx / Caddy | Reverse proxy para HTTPS, SSL automático e gestão do domínio `buscafri.com.br`. |
| **Controle de Versão** | Git & GitHub (`victorseabra75/buscafree`) | Versionamento de código e CI/CD. |
---

### 3. Casos de Uso (Use Cases)

#### UC01 — Ingestão e Processamento Incremental dos Dados do CNPJ
- **Ator:** Pipeline de ETL (Script Python / Cron Job).
- **Descrição:** Baixar periodicamente os arquivos ZIP mensais da Receita Federal, processá-los de forma unitária para economizar disco e atualizar a base no Cloudflare R2.
- **Fluxo Principal:**
  1. Scrape/busca da lista de arquivos ZIP no servidor da Receita Federal.
  2. Para cada arquivo ZIP (Empresas, Estabelecimentos, Sócios, CNAEs, etc.):
     - Download do arquivo ZIP temporário para o disco local.
     - Leitura do CSV interno descompactando via *chunks* em memória.
     - Conversão dos dados formatados e tipados em Parquet.
     - Upload do Parquet para o bucket no Cloudflare R2.
     - Deleção imediata do ZIP e do temporário local.
  3. Atualização dos metadados de controle da última carga (`etl_status.json`).

#### UC02 — Consulta de CNPJ Específico via API
- **Ator:** Cliente / Aplicação Externa.
- **Descrição:** Consultar os dados detalhados de uma empresa a partir do seu CNPJ (14 dígitos).
- **Fluxo Principal:**
  1. Cliente envia `GET /api/v1/cnpj/{cnpj}`.
  2. FastAPI valida o formato do CNPJ.
  3. DuckDB executa query SQL otimizada diretamente sobre os arquivos Parquet.
  4. Retorna JSON estruturado com dados da matriz/filial, razão social, endereço, CNAEs e quadro societário em **< 200ms**.

#### UC03 — Filtros Analíticos e Busca Avançada
- **Ator:** Cliente / Analista.
- **Descrição:** Filtrar empresas por UF, município, CNAE, situação cadastral e porte.
- **Fluxo Principal:**
  1. Cliente envia `GET /api/v1/empresas?uf=BA&cnae=6201500&situacao=2&limit=50`.
  2. FastAPI sanitiza parâmetros.
  3. DuckDB executa a filtragem colunar nos arquivos Parquet com projeção necessária.
  4. Retorna lista paginada de resultados.

---

## 🛠️ Guia de Manutenção e ETL

### 1. Atualização Mensal da Base
Os dados da Receita Federal são atualizados mensalmente. Para atualizar o BuscaFri:

1. **Localizar nova pasta**: Acesse o [Portal de Dados da RFB](https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9) e identifique a pasta do mês (ex: `/2026-10`).
2. **Atualizar Scraper**: Altere a variável `URL` em `scripts/web_scraper.py`.
3. **Execução**:
   ```bash
   python scripts/web_scraper.py
   ```
   O script processará os 37 arquivos padrão: `Cnaes`, `Empresas(0-9)`, `Estabelecimentos(0-9)`, `Socios(0-9)`, `Motivos`, `Municipios`, `Naturezas`, `Paises`, `Qualificacoes` e `Simples`.

### 2. Estratégia de Streaming (Crucial para VPS e2-micro)
Dado o limite de 1GB RAM na GCP:
- **Download**: Um arquivo por vez.
- **Conversão**: O arquivo ZIP deve ser lido e convertido para Parquet sem descompactar tudo no disco, se possível, ou deletando o ZIP imediatamente após a geração do Parquet.
- **Upload**: Enviar para o Cloudflare R2 e remover o arquivo local.

```text
[ Receita Federal (ZIPs) ]
           │
           ▼ (Download 1 por vez)
[ VM GCP - Local Disk Temporário ]
           │
           ▼ (Streaming via DuckDB/Pandas/Polars)
[ Conversão para .parquet ]
           │
           ▼ (Boto3 / S3 API)
[ Cloudflare R2 (Storage Persistente) ]
           │
           ▼ (Leitura / Query Direct)
[ FastAPI + DuckDB Engine ] ──► [ Resposta JSON para o Usuário / buscafri.com.br ]





comando para inicializar o projeto:
.\buscafree\Scripts\activate
uv sync

uv run ruff check .
uv run ruff check . --fix
uv run ruff format
uv run pytest
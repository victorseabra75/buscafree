---
name: buscafri-planner
description: Planejar novas funcionalidades, pesquisar esquemas de dados e gerar PRDs/Specs detalhadas para o projeto BuscaFri. Use quando for iniciar uma nova rota de API, pipeline de dados ou refatoração.
---

# BuscaFri Planner: Cristalização, Pesquisa e PRD

Esta skill guia o planejamento de funcionalidades para a plataforma **BuscaFri** (FastAPI + DuckDB + Playwright + GCP e2-micro).

## Quando Usar
- Planejar novos endpoints da API BuscaFri.
- Mapear novas tabelas de dados da Receita Federal (Empresas, Estabelecimentos, Sócios, Simples, CNAEs).
- Definir arquitetura de armazenamento (DuckDB / Parquet / Cloudflare R2).

## Passo a Passo

### 1. Cristalização da Ideia
Interrogue o desenvolvedor para alinhar o escopo antes de gerar qualquer código:
- **Escopo**: Qual a rota, script ou tabela afetada?
- **Impacto em Recursos**: A operação cabe nos 1GB de RAM da VPS `e2-micro`?
- **Fronteiras**: O que está EXPLICITAMENTE fora do escopo desta tarefa?

### 2. Pesquisa e Caching de Contexto (`research.md`)
- Se a tarefa envolver esquemas de dados da Receita Federal, seletores web complexos ou limites do DuckDB, crie um arquivo temporário `data/research.md`.
- Registre colunas das tabelas, tipos de dados, URLs e XPaths necessários para não gastar janela de contexto pesquisando novamente nas fases de execução.

### 3. Protótipo (Apenas se necessário)
- Se for uma nova estratégia de extração web ou consulta SQL pesada, crie um script isolado na pasta `scripts/prototypes/` para validar a viabilidade técnica antes da Spec final.

### 4. Geração do PRD / Spec
Gere um documento de especificação contendo:
- **Objetivo da Feature**: O que o endpoint/script entregará.
- **Entradas e Saídas**: Schemas Pydantic / Queries SQL exatas.
- **Tratamento de Erros e Limites**: Timeouts, concorrência no DuckDB, memória máxima.
- Apresente ao desenvolvedor e só prossiga após a aprovação explícita.

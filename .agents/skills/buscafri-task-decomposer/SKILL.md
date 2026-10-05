---
name: buscafri-task-decomposer
description: Converter uma PRD/Spec do BuscaFri em tickets e tarefas pequenas, organizadas e paralelas. Use quando a PRD estiver aprovada e pronta para ser dividida em implementação.
---

# BuscaFri Task Decomposer: Quebra em Tickets Atômicos

Esta skill transforma PRDs do BuscaFri em uma lista sequencial ou Kanban de tickets pequenos de fácil execução por agentes de IA.

## Regras Fundamentais
1. **Limite de Lógica por Ticket**: Cada ticket deve resultar em no máximo **500 linhas de lógica de código** (arquivos de teste, schemas JSON/YAML e documentação não contam para o limite).
2. **Dependências Bloqueantes**: Identifique explicitamente quais tickets dependem da conclusão de outros (ex: *Criação de Tabela DuckDB* bloqueia *Endpoint de Consulta de CNPJ*).
3. **Foco no BuscaFri**: Mantenha a separação clara entre as camadas do projeto (`scripts/` para ingestão/scraping, `app/` para FastAPI/DuckDB, `tests/` para testes).

## Formato de Saída dos Tickets
Para cada ticket gerado, apresente a seguinte estrutura:
- **[TICKET-ID] Título Curto e Objetivo**
- **Camada Afetada**: `Scraper` | `DuckDB Ingestion` | `FastAPI Endpoint` | `R2 Backup`
- **Dependências**: [Tickets que precisam ser concluídos antes]
- **Arquivos a Modificar/Criar**: Lista dos caminhos exatos
- **Critério de Aceite**: O que precisa funcionar para considerar o ticket pronto.

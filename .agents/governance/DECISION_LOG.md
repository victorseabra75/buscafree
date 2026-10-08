# BuscaFri --- Registro de Decisões Técnicas

Este arquivo funciona como índice das decisões técnicas relevantes.

Decisões arquiteturais completas devem ficar em `.agents/adr/`.

## Decisões já consolidadas

### ADR-001 --- Bare Metal em vez de Docker

**Status:** Aceito

A produção utiliza Bare Metal para reduzir o consumo de recursos na VM
GCP e2-micro.

### ADR-002 --- Processamento ETL em streaming

**Status:** Aceito

Arquivos grandes da Receita Federal devem ser processados sem carregar a
base inteira em memória.

### ADR-003 --- Parquet como formato analítico

**Status:** Aceito

Parquet é utilizado como formato persistente para consultas analíticas
com DuckDB.

### ADR-004 --- DuckDB + Cloudflare R2

**Status:** Aceito

A arquitetura de produção utiliza DuckDB para consultar Parquet
armazenado no Cloudflare R2, evitando manter toda a base local na VPS.

### ADR-005 --- SQL parametrizado

**Status:** Aceito

Valores fornecidos pelo usuário não devem ser concatenados diretamente
em SQL.

### ADR-006 --- Configuração por ambiente

**Status:** Em consolidação

Caminhos e credenciais dependentes de ambiente devem ser fornecidos por
configuração, evitando defaults locais silenciosos em produção.

### ADR-007 --- Fluxo de Dados e Particionamento

**Status:** Aceito

Manter o fluxo atual de dados com Parquet corrigido, estabelecimentos
particionados por UF, Hive partitioning e compressão SNAPPY.

### ADR-008 --- Tipagem Física VARCHAR em Parquet

**Status:** Aceito

Manter a tipagem física atual dos Parquet como VARCHAR neste momento,
sem regenerar os arquivos apenas por causa da diferença entre o
schema lógico e o schema físico.

### ADR-009 --- Arquitetura do Backend

**Status:** Aceito

Manter FastAPI + DuckDB + httpfs como a arquitetura atual do backend,
permitindo consultas eficientes diretamente no Cloudflare R2.

### ADR-010 --- Ambiente Técnico de Execução

**Status:** Aceito

Manter a execução local + Cloudflare R2 como o ambiente técnico
atualmente utilizável, enquanto a VPS de produção permanece
indisponível.

### ADR-011 --- Estrutura de Documentação

**Status:** Aceito

Manter a documentação separada entre fonte de verdade, estado atual,
divergências, decisões e histórico para garantir a governança do
projeto.

### ADR-012 — Consolidação das skills em .agents/

**Status:** Aceita

**Contexto:**
O projeto possuía uma estrutura .continue/ com skills de assistentes/
editores que se sobrepunha às skills mantidas em .agents/skills/.
Foram identificados 101 arquivos em .continue/skills/ que pertenciam
ao ecossistema Continue/Matt Pocock e não ao core do BuscaFri.

**Decisão:**
Remover deliberadamente a estrutura .continue/ e consolidar as skills
oficiais do projeto em:
.agents/skills/
A estrutura .continue/ não faz mais parte da arquitetura oficial do
BuscaFri.

**Motivação:**
- eliminar duplicidade;
- reduzir estruturas redundantes;
- centralizar as skills utilizadas pelo projeto;
- manter .agents/ como estrutura oficial de contexto, tarefas e skills;
- evitar manter duas fontes de skills para os agentes.

**Consequências:**
- .continue/ permanece removido;
- os 101 arquivos deletados não devem ser restaurados;
- .agents/skills/ passa a ser a única estrutura oficial de skills;
- novas skills do projeto devem ser adicionadas em .agents/skills/;
- referências futuras a .continue/ não devem ser criadas.

## Regra

Quando uma nova alteração mudar uma dessas decisões, o agente deve criar
um novo ADR ou atualizar explicitamente o ADR existente.

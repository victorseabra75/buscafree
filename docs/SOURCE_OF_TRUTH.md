# Matriz de Fontes de Verdade - Projeto BuscaFri

Este documento estabelece a hierarquia de fontes de verdade para o projeto. Em caso de divergência, esta matriz define qual documento deve ser consultado primeiro.

## 1. Tabela da Matriz de Fontes de Verdade

| Domínio | Fonte Primária | Fonte Secundária | Regra de Precedência |
| :--- | :--- | :--- | :--- |
| Regras de Agentes | `AGENTS.md` | - | Primária |
| Contexto Arquitetural | `.agents/CONTEXT.md` | `.agents/governance/DECISION_LOG.md` | Primária |
| Tarefas | `.agents/tasks.md` | `PROJECT_STATUS.md` | Primária |
| Workflow | `.agents/governance/DEVELOPMENT_WORKFLOW.md` | `AGENTS.md` | Primária |
| Decisões Arquiteturais | `.agents/governance/adr/` | `.agents/governance/DECISION_LOG.md` | Primária |
| Histórico | `.agents/governance/CHANGELOG.md` | - | Primária |
| Documentação | `README.md` | `docs/` | Primária |
| Código | Implementação | Testes | Não verificado |
| Testes | Testes | Implementação | Não verificado |

*Nota: Para Código e Testes, a realidade executável ainda precisa ser validada em etapa posterior.*

## 2. Como resolver conflitos

Quando documentação e implementação divergirem, **NÃO corrigir automaticamente**.

O agente deve seguir o protocolo:
1.  **Registrar a divergência** no `DECISION_LOG.md` ou issue correspondente.
2.  **Verificar** na ordem:
    - Código atual;
    - Testes;
    - Configuração efetiva;
    - Documentação normativa (`CONTEXT.md`, `ADR`);
    - Documentação operacional (`DEVELOPMENT_WORKFLOW.md`);
    - Documentação geral (`README.md`).
3.  Se a questão não puder ser resolvida com as fontes listadas, marcar o componente/funcionalidade como: **NÃO VERIFICADO**.

## 3. Consolidação

*Consolidação realizada na tarefa 0.10.*

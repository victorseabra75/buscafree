---
name: buscafri-executor-qa
description: Executar tickets individuais do BuscaFri, aplicar desenvolvimento orientado a testes (TDD) e validar o código com suítes de teste e QA. Use para codificar e testar tarefas específicas.
---

# BuscaFri Executor & QA: Execução, TDD e Validação

Esta skill é responsável por codificar um ticket por vez no BuscaFri, garantindo qualidade via testes automatizados e validações de ambiente.

## Quando Usar
- Executar a implementação de um ticket específico da lista.
- Escrever e rodar testes unitários com Pytest.
- Debugar e corrigir falhas de execução no Scraper, DuckDB ou FastAPI.

## Fluxo de Execução e TDD
1. **Carregar Contexto Focado**:
- Leia apenas a PRD e as instruções do ticket atual. Ignore outros módulos que não influenciam esta tarefa.
2. **Test-Driven Development (TDD)**:
- Escreva primeiro o teste automatizado em `tests/` para o comportamento esperado (ex: teste da rota `/cnpj/{cnpj}` ou teste de conversão de CSV em Parquet).
- Execute o teste com `pytest` e confirme que ele **falha** (comportamento correto do TDD).
3. **Implementação**:
- Escreva o código mínimo necessário no módulo correspondente (`scripts/` ou `app/`) para satisfazer o teste.
4. **Loop de Correção e QA**:
- Rode o `pytest` no terminal integrado.
- Se houver erro, analise os logs do terminal, faça o ajuste fino no código e execute novamente até que todos os testes passem.
- Verifique o uso de memória e confirme que não há vazamento de recursos (conexões abertas no DuckDB ou instâncias do Playwright sem fechamento).

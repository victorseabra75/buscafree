# BuscaFri --- Changelog Técnico

Registro resumido de alterações relevantes para manutenção do projeto.

## Formato

Cada entrada deve informar:

-   data;
-   tipo da alteração;
-   descrição;
-   arquivos principais;
-   validação.

Tipos:

-   `feat`
-   `fix`
-   `refactor`
-   `test`
-   `docs`
-   `chore`

## 2026

### Configuração e API

-   Centralização da configuração local/produção está sendo consolidada.
-   A API de busca utiliza caminhos configuráveis para
    `estabelecimentos` e `empresas`.
-   Testes da API particionada devem utilizar as rotas completas
    `/api/v1/...`.
-   Testes locais da API devem usar os Parquets locais corrigidos quando
    esse for o objetivo do teste.
-   Respostas da API tratam valores `NaN` antes da validação Pydantic.

### Dados

-   Parquets corrigidos foram validados.
-   Os arquivos de `estabelecimentos` foram particionados por UF.
-   A auditoria do particionamento confirmou preservação de registros e
    ausência de violações de isolamento.

> Este changelog deve ser atualizado somente com fatos verificados no
> código, testes ou registros do projeto.

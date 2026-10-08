# BUSCAFRI --- Mapeamento de Dados e Guia para Filtros Avançados do Streamlit

## 1. Objetivo

Este documento descreve as 10 tabelas disponíveis no Cloudflare R2, suas
colunas, tipos lógicos conhecidos, conteúdo esperado e relacionamentos.

O objetivo é servir como **fonte de verdade para o agente responsável
pelo desenvolvimento dos filtros avançados do Streamlit**.

> **Atenção:** o mapeamento lógico fornecido informa tipos como `DATE`,
> `DOUBLE` e `INTEGER`, porém o `DESCRIBE` executado diretamente nos
> Parquet retornou `VARCHAR` para todas as colunas. Portanto, o código
> da aplicação **não deve assumir que datas, valores monetários ou
> inteiros já estão fisicamente tipados**. Antes de filtrar, deve
> verificar/castar de forma segura, por exemplo com `TRY_CAST`.

------------------------------------------------------------------------

# 2. Visão geral das tabelas

  -----------------------------------------------------------------------
  Tabela                              Função
  ----------------------------------- -----------------------------------
  `cnaes`                             Cadastro de códigos CNAE e suas
                                      descrições

  `empresas`                          Dados cadastrais da empresa pelo
                                      CNPJ básico

  `estabelecimentos`                  Dados de cada estabelecimento,
                                      endereço, atividade, situação e
                                      contato

  `motivos`                           Tabela de códigos de motivo de
                                      situação cadastral

  `municipios`                        Tabela de códigos de municípios

  `naturezas`                         Tabela de natureza jurídica

  `paises`                            Tabela de países

  `qualificacoes`                     Tabela de qualificações

  `simples`                           Dados de opção pelo Simples
                                      Nacional e MEI

  `socios`                            Dados dos sócios e representantes
                                      legais
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 3. Mapeamento detalhado das tabelas

## 3.1 `cnaes`

### Finalidade

Tabela de referência para códigos CNAE.

  Coluna        Tipo lógico   Conteúdo
  ------------- ------------- --------------------------------
  `codigo`      VARCHAR       Código da atividade econômica
  `descricao`   VARCHAR       Descrição textual da atividade

### Uso no Streamlit

Filtros: - CNAE principal; - CNAE secundário; - busca por código CNAE; -
busca por descrição CNAE.

### Relacionamento

`cnaes.codigo` relaciona-se com:

``` text
estabelecimentos.cnae_fiscal_principal
estabelecimentos.cnae_fiscal_secundaria
```

### Observação

`cnae_fiscal_secundaria` está armazenado em uma única coluna e pode
conter múltiplos códigos. O filtro de CNAE secundário não deve usar
simplesmente igualdade (`=`) se houver vários códigos na mesma célula.

------------------------------------------------------------------------

# 3.2 `empresas`

### Finalidade

Tabela principal de informações cadastrais da empresa.

  -------------------------------------------------------------------------------
  Coluna                          Tipo lógico             Conteúdo
  ------------------------------- ----------------------- -----------------------
  `cnpj_basico`                   VARCHAR                 Identificador básico da
                                                          empresa

  `razao_social`                  VARCHAR                 Razão social

  `natureza_juridica`             VARCHAR                 Código da natureza
                                                          jurídica

  `qualificacao_responsavel`      VARCHAR                 Código da qualificação
                                                          do responsável

  `capital_social`                DOUBLE                  Capital social

  `porte_empresa`                 VARCHAR                 Porte da empresa

  `ente_federativo_responsavel`   VARCHAR                 Ente federativo
                                                          responsável, quando
                                                          aplicável
  -------------------------------------------------------------------------------

### Filtros possíveis

-   CNPJ básico;
-   razão social;
-   natureza jurídica;
-   qualificação do responsável;
-   capital social mínimo;
-   capital social máximo;
-   porte da empresa;
-   ente federativo responsável.

### Relacionamentos

Chave principal de relacionamento:

``` text
empresas.cnpj_basico
        |
        +---- estabelecimentos.cnpj_basico
        |
        +---- simples.cnpj_basico
        |
        +---- socios.cnpj_basico
```

------------------------------------------------------------------------

# 3.3 `estabelecimentos`

### Finalidade

É a tabela mais importante para filtros avançados, pois contém endereço,
atividade econômica, situação cadastral, contatos e identificação de
matriz/filial.

  -------------------------------------------------------------------------------
  Coluna                          Tipo lógico             Conteúdo
  ------------------------------- ----------------------- -----------------------
  `cnpj_basico`                   VARCHAR                 CNPJ básico da empresa

  `cnpj_ordem`                    VARCHAR                 Número de ordem do
                                                          estabelecimento

  `cnpj_dv`                       VARCHAR                 Dígitos verificadores

  `identificador_matriz_filial`   VARCHAR                 Identifica matriz ou
                                                          filial

  `nome_fantasia`                 VARCHAR                 Nome fantasia

  `situacao_cadastral`            VARCHAR                 Código da situação
                                                          cadastral

  `data_situacao_cadastral`       DATE                    Data da situação
                                                          cadastral

  `motivo_situacao_cadastral`     VARCHAR                 Código do motivo da
                                                          situação

  `nome_cidade_exterior`          VARCHAR                 Cidade no exterior,
                                                          quando aplicável

  `pais`                          VARCHAR                 Código do país

  `data_inicio_atividade`         DATE                    Data de início da
                                                          atividade

  `cnae_fiscal_principal`         VARCHAR                 CNAE principal

  `cnae_fiscal_secundaria`        VARCHAR                 CNAEs secundários

  `tipo_logradouro`               VARCHAR                 Tipo do logradouro

  `logradouro`                    VARCHAR                 Logradouro

  `numero`                        VARCHAR                 Número

  `complemento`                   VARCHAR                 Complemento

  `bairro`                        VARCHAR                 Bairro

  `cep`                           VARCHAR                 CEP

  `uf`                            VARCHAR                 Unidade federativa

  `municipio`                     VARCHAR                 Código do município

  `ddd_1`                         VARCHAR                 DDD do telefone
                                                          principal

  `telefone_1`                    VARCHAR                 Telefone principal

  `ddd_2`                         VARCHAR                 DDD do segundo telefone

  `telefone_2`                    VARCHAR                 Segundo telefone

  `ddd_fax`                       VARCHAR                 DDD do fax

  `fax`                           VARCHAR                 Fax

  `correio_eletronico`            VARCHAR                 E-mail

  `situacao_especial`             VARCHAR                 Situação especial

  `data_situacao_especial`        DATE                    Data da situação
                                                          especial
  -------------------------------------------------------------------------------

### Filtros avançados possíveis

#### Identificação

-   CNPJ;
-   CNPJ básico;
-   nome fantasia;
-   matriz/filial.

#### Situação

-   situação cadastral;
-   motivo da situação;
-   período da situação cadastral;
-   situação especial;
-   período da situação especial.

#### Atividade econômica

-   CNAE principal;
-   CNAE secundário;
-   descrição do CNAE.

#### Localização

-   UF;
-   município;
-   bairro;
-   CEP;
-   logradouro;
-   cidade no exterior;
-   país.

#### Datas

-   início da atividade;
-   data da situação cadastral;
-   data da situação especial.

#### Contatos

-   possui telefone;
-   possui segundo telefone;
-   possui fax;
-   possui e-mail;
-   DDD.

------------------------------------------------------------------------

# 3.4 `motivos`

### Finalidade

Tabela de referência para os motivos de situação cadastral.

  Coluna        Tipo lógico   Conteúdo
  ------------- ------------- ---------------------
  `codigo`      VARCHAR       Código do motivo
  `descricao`   VARCHAR       Descrição do motivo

### Relacionamento

``` text
motivos.codigo
    ↓
estabelecimentos.motivo_situacao_cadastral
```

### Uso no Streamlit

O usuário deve poder selecionar a descrição do motivo, enquanto a
consulta utiliza o código.

------------------------------------------------------------------------

# 3.5 `municipios`

### Finalidade

Tabela de referência de municípios.

  Coluna        Tipo lógico   Conteúdo
  ------------- ------------- ---------------------
  `codigo`      VARCHAR       Código do município
  `descricao`   VARCHAR       Nome do município

### Relacionamento

``` text
municipios.codigo
    ↓
estabelecimentos.municipio
```

### Uso no Streamlit

Fluxo recomendado:

``` text
UF
 ↓
Municípios daquela UF
 ↓
estabelecimentos.municipio
```

O filtro de município deve apresentar o nome (`descricao`) ao usuário,
mas filtrar pelo código (`codigo`).

------------------------------------------------------------------------

# 3.6 `naturezas`

### Finalidade

Tabela de referência de naturezas jurídicas.

  Coluna        Tipo lógico   Conteúdo
  ------------- ------------- --------------------------------
  `codigo`      VARCHAR       Código da natureza jurídica
  `descricao`   VARCHAR       Descrição da natureza jurídica

### Relacionamento

``` text
naturezas.codigo
    ↓
empresas.natureza_juridica
```

### Uso no Streamlit

Mostrar a descrição para o usuário e utilizar o código na consulta.

------------------------------------------------------------------------

# 3.7 `paises`

### Finalidade

Tabela de referência de países.

  Coluna        Tipo lógico   Conteúdo
  ------------- ------------- ----------------
  `codigo`      VARCHAR       Código do país
  `descricao`   VARCHAR       Nome do país

### Relacionamentos

``` text
paises.codigo
    ↓
estabelecimentos.pais

paises.codigo
    ↓
socios.pais
```

------------------------------------------------------------------------

# 3.8 `qualificacoes`

### Finalidade

Tabela de referência de qualificações.

  Coluna        Tipo lógico   Conteúdo
  ------------- ------------- ---------------------------
  `codigo`      VARCHAR       Código da qualificação
  `descricao`   VARCHAR       Descrição da qualificação

### Relacionamentos

``` text
qualificacoes.codigo
    ↓
empresas.qualificacao_responsavel

qualificacoes.codigo
    ↓
socios.qualificacao_socio

qualificacoes.codigo
    ↓
socios.qualificacao_representante
```

------------------------------------------------------------------------

# 3.9 `simples`

### Finalidade

Informa opção pelo Simples Nacional e MEI.

  Coluna                    Tipo lógico   Conteúdo
  ------------------------- ------------- ---------------------------------
  `cnpj_basico`             VARCHAR       CNPJ básico
  `opcao_simples`           VARCHAR       Indicador de opção pelo Simples
  `data_opcao_simples`      DATE          Data de opção pelo Simples
  `data_exclusao_simples`   DATE          Data de exclusão do Simples
  `opcao_mei`               VARCHAR       Indicador de opção pelo MEI
  `data_opcao_mei`          DATE          Data de opção pelo MEI
  `data_exclusao_mei`       DATE          Data de exclusão do MEI

### Relacionamento

``` text
simples.cnpj_basico
    ↓
empresas.cnpj_basico
```

### Filtros avançados

-   é optante pelo Simples;
-   não é optante pelo Simples;
-   é MEI;
-   não é MEI;
-   data de opção pelo Simples;
-   período de exclusão do Simples;
-   data de opção pelo MEI;
-   período de exclusão do MEI.

### Regra importante

Como `simples` é relacionada ao CNPJ básico, uma empresa pode ser
localizada pela tabela `simples` e depois relacionada aos seus
estabelecimentos.

------------------------------------------------------------------------

# 3.10 `socios`

### Finalidade

Contém informações dos sócios e representantes legais.

  ------------------------------------------------------------------------------
  Coluna                         Tipo lógico             Conteúdo
  ------------------------------ ----------------------- -----------------------
  `cnpj_basico`                  VARCHAR                 CNPJ básico da empresa

  `identificador_socio`          VARCHAR                 Tipo/identificador do
                                                         sócio

  `nome_socio`                   VARCHAR                 Nome do sócio

  `cnpj_cpf_socio`               VARCHAR                 CPF/CNPJ do sócio

  `qualificacao_socio`           VARCHAR                 Código da qualificação
                                                         do sócio

  `data_entrada_sociedade`       DATE                    Data de entrada na
                                                         sociedade

  `pais`                         VARCHAR                 Código do país

  `representante_legal`          VARCHAR                 Indicador/dado do
                                                         representante legal

  `nome_representante`           VARCHAR                 Nome do representante

  `qualificacao_representante`   VARCHAR                 Código da qualificação
                                                         do representante

  `faixa_etaria`                 INTEGER                 Faixa etária codificada
  ------------------------------------------------------------------------------

### Relacionamento

``` text
socios.cnpj_basico
    ↓
empresas.cnpj_basico
```

### Filtros avançados

-   nome do sócio;
-   identificação do sócio;
-   qualificação do sócio;
-   país;
-   data de entrada na sociedade;
-   representante legal;
-   nome do representante;
-   qualificação do representante;
-   faixa etária.

------------------------------------------------------------------------

# 4. Mapa de relacionamentos

## Relação central

O campo central do modelo é:

``` text
cnpj_basico
```

A estrutura principal é:

``` text
                    ┌──────────────┐
                    │   empresas   │
                    │ cnpj_basico  │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
│ estabelecimentos│ │   simples    │ │    socios    │
│  cnpj_basico    │ │ cnpj_basico  │ │ cnpj_basico  │
└────────┬────────┘ └──────────────┘ └──────────────┘
         │
         ├── municipio → municipios.codigo
         │
         ├── cnae_fiscal_principal → cnaes.codigo
         │
         ├── cnae_fiscal_secundaria → cnaes.codigo
         │
         ├── natureza jurídica ← empresas
         │
         ├── motivo situação → motivos.codigo
         │
         └── pais → paises.codigo

empresas.natureza_juridica
        ↓
naturezas.codigo

empresas.qualificacao_responsavel
        ↓
qualificacoes.codigo

socios.qualificacao_socio
        ↓
qualificacoes.codigo

socios.qualificacao_representante
        ↓
qualificacoes.codigo
```

------------------------------------------------------------------------

# 5. Filtros que o Streamlit deve oferecer

## Grupo A --- Empresa

-   Razão social
-   Nome fantasia
-   CNPJ
-   Porte
-   Capital social mínimo
-   Capital social máximo
-   Natureza jurídica
-   Ente federativo responsável

## Grupo B --- Estabelecimento

-   Matriz / filial
-   Situação cadastral
-   Motivo da situação
-   Data da situação
-   Data de início da atividade
-   Situação especial
-   Data da situação especial

## Grupo C --- Atividade econômica

-   CNAE principal
-   CNAE secundário
-   Pesquisa por código CNAE
-   Pesquisa por descrição CNAE

## Grupo D --- Localização

-   UF
-   Município
-   Bairro
-   CEP
-   Logradouro
-   País

## Grupo E --- Contato

-   Possui telefone
-   Possui segundo telefone
-   Possui e-mail
-   Possui fax
-   DDD

## Grupo F --- Simples / MEI

-   Optante pelo Simples
-   Não optante pelo Simples
-   MEI
-   Não MEI
-   Período de opção
-   Período de exclusão

## Grupo G --- Sócios

-   Nome do sócio
-   CPF/CNPJ do sócio
-   Qualificação
-   País
-   Data de entrada
-   Representante legal
-   Faixa etária

------------------------------------------------------------------------

# 6. Filtros que precisam de JOIN

Nem todo filtro deve consultar diretamente `estabelecimentos`.

### Natureza jurídica

``` sql
empresas
JOIN naturezas
  ON empresas.natureza_juridica = naturezas.codigo
```

### Município

``` sql
estabelecimentos
JOIN municipios
  ON estabelecimentos.municipio = municipios.codigo
```

### CNAE

``` sql
estabelecimentos
JOIN cnaes
  ON estabelecimentos.cnae_fiscal_principal = cnaes.codigo
```

### Motivo

``` sql
estabelecimentos
JOIN motivos
  ON estabelecimentos.motivo_situacao_cadastral = motivos.codigo
```

### Simples/MEI

``` sql
empresas
JOIN simples
  ON empresas.cnpj_basico = simples.cnpj_basico
```

### Sócios

``` sql
empresas
JOIN socios
  ON empresas.cnpj_basico = socios.cnpj_basico
```

------------------------------------------------------------------------

# 7. Filtros dependentes

O Streamlit deve evitar carregar listas gigantes desnecessariamente.

## UF → Município

Fluxo:

``` text
Selecionar UF
     ↓
buscar municípios daquela UF
     ↓
mostrar somente municípios aplicáveis
```

## CNAE → descrição

Fluxo:

``` text
Código CNAE
     ↓
buscar descrição em cnaes
```

ou:

``` text
Descrição
     ↓
buscar código
```

## Situação → Motivo

O motivo pode ser filtrado após a seleção da situação cadastral.

------------------------------------------------------------------------

# 8. Tipos de filtros recomendados

  Tipo de dado         Widget recomendado
  -------------------- ---------------------------------
  Código               Selectbox / multiselect / texto
  Descrição            Selectbox pesquisável
  Texto livre          Text input
  Booleano/indicador   Checkbox
  Lista de opções      Multiselect
  Data                 Date input / intervalo de datas
  Número               Number input / slider
  Capital social       Intervalo numérico
  UF                   Selectbox
  Município            Selectbox dependente
  CNAE                 Selectbox pesquisável
  CNPJ                 Text input
  Telefone/e-mail      Checkbox de existência

------------------------------------------------------------------------

# 9. Regras para construção das consultas

## 9.1 Nunca concatenar diretamente valores do usuário

Evitar:

``` python
sql += f"AND est.uf = '{uf}'"
```

Preferir parâmetros:

``` python
where_clauses.append("est.uf = ?")
parameters.append(uf)
```

------------------------------------------------------------------------

## 9.2 Filtros opcionais

Cada filtro deve ser aplicado somente quando o usuário preenchê-lo.

Exemplo:

``` text
UF = BA
Município = Seabra
```

gera:

``` sql
WHERE est.uf = ?
  AND est.municipio = ?
```

Se o usuário não selecionar município:

``` sql
WHERE est.uf = ?
```

------------------------------------------------------------------------

# 10. Datas

Embora o mapeamento lógico indique `DATE`, o `DESCRIBE` dos Parquet
retornou `VARCHAR`.

Portanto, para filtros de datas, utilizar conversão segura.

Exemplo conceitual:

``` sql
TRY_CAST(est.data_inicio_atividade AS DATE)
```

Não assumir diretamente:

``` sql
est.data_inicio_atividade >= ?
```

sem confirmar o tipo físico.

Aplicar a mesma regra para:

``` text
data_situacao_cadastral
data_inicio_atividade
data_situacao_especial
data_opcao_simples
data_exclusao_simples
data_opcao_mei
data_exclusao_mei
data_entrada_sociedade
```

------------------------------------------------------------------------

# 11. Capital social

O mapeamento lógico indica:

``` text
capital_social → DOUBLE
```

mas o schema físico retornado pelo Parquet indica `VARCHAR`.

Para filtros de faixa:

``` sql
TRY_CAST(emp.capital_social AS DOUBLE)
```

Exemplo:

``` sql
TRY_CAST(emp.capital_social AS DOUBLE) >= ?
AND TRY_CAST(emp.capital_social AS DOUBLE) <= ?
```

------------------------------------------------------------------------

# 12. Faixa etária

O mapeamento lógico indica:

``` text
faixa_etaria → INTEGER
```

mas o schema físico retornado indica `VARCHAR`.

Portanto, caso seja necessário comparar numericamente:

``` sql
TRY_CAST(s.faixa_etaria AS INTEGER)
```

------------------------------------------------------------------------

# 13. Telefones e e-mail

Filtros de existência devem considerar valores vazios.

Não utilizar somente:

``` sql
telefone_1 IS NOT NULL
```

Preferir:

``` sql
telefone_1 IS NOT NULL
AND TRIM(telefone_1) <> ''
```

Para e-mail:

``` sql
correio_eletronico IS NOT NULL
AND TRIM(correio_eletronico) <> ''
```

------------------------------------------------------------------------

# 14. CNAE secundário

`cnae_fiscal_secundaria` pode conter múltiplos códigos na mesma coluna.

Portanto, o filtro deve ser implementado considerando o formato real dos
dados.

Antes de definir a expressão SQL definitiva, inspecionar exemplos reais:

``` sql
SELECT cnae_fiscal_secundaria
FROM 's3://buscafri-data/estabelecimentos/*.parquet'
WHERE cnae_fiscal_secundaria IS NOT NULL
LIMIT 20
```

Não assumir que o conteúdo é uma única string contendo apenas um CNAE.

------------------------------------------------------------------------

# 15. CNPJ completo

O CNPJ completo pode ser reconstruído a partir de:

``` text
cnpj_basico
cnpj_ordem
cnpj_dv
```

Conceitualmente:

``` sql
cnpj_basico || cnpj_ordem || cnpj_dv
```

Antes de apresentar ao usuário, verificar necessidade de padronização
com zeros à esquerda.

------------------------------------------------------------------------

# 16. Resultado esperado no Streamlit

O usuário deve conseguir combinar vários filtros.

Exemplo:

``` text
LOCALIZAÇÃO
UF: BA
Município: Seabra

EMPRESA
Porte: Pequena
Capital social: R$ 50.000 a R$ 500.000

ATIVIDADE
CNAE principal: determinado CNAE

SITUAÇÃO
Situação cadastral: ATIVA

CONTATO
☑ Possui telefone
☑ Possui e-mail

REGIME
☑ Simples Nacional
☐ MEI
```

A aplicação deve transformar essas escolhas em uma única consulta
parametrizada.

------------------------------------------------------------------------

# 17. Arquitetura recomendada para os filtros

Separar:

``` text
Streamlit UI
    ↓
estado dos filtros
    ↓
construtor de filtros
    ↓
SQL parametrizado
    ↓
DuckDB
    ↓
Parquet no R2
```

Evitar colocar toda a construção SQL diretamente dentro do código dos
widgets Streamlit.

Idealmente:

``` text
app/
├── ui/
│   └── filtros.py
├── services/
│   └── busca.py
└── core/
    └── database.py
```

------------------------------------------------------------------------

# 18. Regra fundamental para o agente

Antes de implementar qualquer filtro:

1.  verificar o nome exato da coluna;
2.  verificar o tipo lógico;
3.  considerar o tipo físico real do Parquet;
4.  identificar a tabela de origem;
5.  identificar se precisa de JOIN;
6.  utilizar parâmetros SQL;
7.  testar o filtro isoladamente;
8.  testar combinações de filtros;
9.  verificar desempenho no DuckDB/R2.

**Não inventar colunas, relacionamentos ou códigos de domínio.**

Quando um filtro depender de códigos cuja descrição está em uma tabela
de referência, o usuário deve visualizar a descrição, mas a consulta
deve utilizar o código correspondente.

------------------------------------------------------------------------

# 19. Resumo operacional para o agente

### Tabelas principais

``` text
empresas
estabelecimentos
simples
socios
```

### Tabelas de referência

``` text
cnaes
motivos
municipios
naturezas
paises
qualificacoes
```

### Chave de empresa

``` text
cnpj_basico
```

### Principal tabela para localização e atividade

``` text
estabelecimentos
```

### Principal tabela para dados corporativos

``` text
empresas
```

### Principal tabela para regime tributário

``` text
simples
```

### Principal tabela para sócios

``` text
socios
```

### Principal cuidado técnico

``` text
Tipos lógicos != necessariamente tipos físicos dos Parquet
```

Os Parquet atualmente retornaram `VARCHAR` no `DESCRIBE` para todas as
colunas verificadas. Portanto, usar `TRY_CAST` quando uma operação
exigir `DATE`, `DOUBLE` ou `INTEGER`, até que o schema físico seja
confirmado/corrigido.

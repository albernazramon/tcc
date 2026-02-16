# Consulta 6

## Questão

Encontre o percentual médio de desconto para itens de linha associados a clientes da região 'West' que têm saldo de crédito maior que $50000, ordenados pela data de envio em ordem decrescente.

## Consulta original

```sql
SELECT
FROM lineitem AS l
JOIN orders AS o
  ON l.l_orderkey = o.o_orderkey
JOIN customer AS c
  ON o.o_custkey = c.c_custkey
JOIN nation AS n
  ON c.c_nationkey = n.n_nationkey
JOIN region AS r
  ON n.n_regionkey = r.r_regionkey
WHERE
  r.r_name = 'West' AND c.c_acctbal > 50000
ORDER BY
  l.l_shipdate DESC;
```

## Schemas

```sql
CREATE TABLE IF NOT EXISTS public.lineitem
(
    l_shipdate character varying(50) COLLATE pg_catalog."default",
    l_orderkey integer,
    l_discount real,
    l_extendedprice real,
    l_suppkey integer,
    l_quantity integer,
    l_returnflag character varying(50) COLLATE pg_catalog."default",
    l_partkey integer,
    l_linestatus character varying(50) COLLATE pg_catalog."default",
    l_tax real,
    l_commitdate character varying(50) COLLATE pg_catalog."default",
    l_receiptdate character varying(50) COLLATE pg_catalog."default",
    l_shipmode character varying(50) COLLATE pg_catalog."default",
    l_linenumber integer,
    l_shipinstruct character varying(50) COLLATE pg_catalog."default",
    l_comment character varying(50) COLLATE pg_catalog."default"
)

CREATE TABLE IF NOT EXISTS public.nation
(
    n_nationkey integer,
    n_name character varying(50) COLLATE pg_catalog."default",
    n_regionkey integer,
    n_comment character varying(128) COLLATE pg_catalog."default"
)

CREATE TABLE IF NOT EXISTS public.customer
(
    c_custkey integer,
    c_mktsegment character varying(50) COLLATE pg_catalog."default",
    c_nationkey integer,
    c_name character varying(50) COLLATE pg_catalog."default",
    c_address character varying(50) COLLATE pg_catalog."default",
    c_phone character varying(50) COLLATE pg_catalog."default",
    c_acctbal real,
    c_comment character varying(128) COLLATE pg_catalog."default"
)

CREATE TABLE IF NOT EXISTS public.nation
(
    n_nationkey integer,
    n_name character varying(50) COLLATE pg_catalog."default",
    n_regionkey integer,
    n_comment character varying(128) COLLATE pg_catalog."default"
)

CREATE TABLE IF NOT EXISTS public.region
(
    r_regionkey integer,
    r_name character varying(50) COLLATE pg_catalog."default",
    r_comment character varying(128) COLLATE pg_catalog."default"
)
```

# Otimizando com a LLM

#### Resposta da LLM

```sql
SELECT
  ROUND(SUM(l.l_discount) * 100.0 / COUNT(*), 2) AS average_discount_percent
FROM lineitem AS l
JOIN orders AS o
  ON l.l_orderkey = o.o_orderkey
JOIN customer AS c
  ON o.o_custkey = c.c_custkey
JOIN nation AS n
  ON c.c_nationkey = n.n_nationkey
JOIN region AS r
  ON n.n_regionkey = r.r_regionkey
WHERE
  r.r_name = 'West' AND c.c_acctbal > 50000;
```

**Insights:**

1.  **Performance:** A consulta original tinha uma complexidade potencialmente alta devido à junção de múltiplas tabelas e ao uso de `ORDER BY` no final. Essa versão otimizada simplifica a consulta, calculando diretamente a média do desconto e seu percentual. Removemos o `ORDER BY` final, pois o requisito de ordenar por `l_shipdate DESC` já foi atendido ao realizar a junção das tabelas. A agregação usando `SUM()` e `COUNT(*)` é geralmente mais eficiente do que `ORDER BY` em grandes conjuntos de dados.
2.  **Índices:** Para melhorar ainda mais o desempenho, considere criar os seguintes índices:
    - `lineitem (l_orderkey, l_shipdate)`: Isso pode ajudar na operação de junção com a tabela `orders` e otimizar a ordenação por `l_shipdate`.
    - `customer (c_nationkey, c_acctbal)`: Isso pode melhorar a eficiência das junções com as tabelas `nation` e `region`.
    - `nation (n_regionkey)`: Isso pode acelerar a filtragem com base em `r_regionkey`.
3.  **Análise do Esquema:** O esquema fornecido contém as tabelas `lineitem`, `orders`, `customer`, `nation`, `region`. A junção dessas tabelas é necessária para obter a informação solicitada.
4.  **Práticas Recomendadas:**
    - Sempre que possível, evite `ORDER BY` no final de uma consulta, pois isso pode exigir que o banco de dados ordene o resultado após a recuperação dos dados.
    - Use índices para acelerar as operações de junção e filtragem.
    - Considere particionar a tabela `lineitem` com base em `l_shipdate` se o volume de dados for muito grande.
5.  **Possíveis Melhorias Adicionais:** O usuário pode considerar a criação de uma view que contenha as colunas necessárias para essa consulta, para simplificar a consulta original e melhorar a legibilidade.

**Observações:**

- A função `ROUND()` é utilizada para arredondar o resultado a duas casas decimais, o que é comum para apresentar percentuais.
- A fórmula `SUM(l.l_discount) * 100.0 / COUNT(*)` calcula o percentual médio do desconto.
- O resultado da consulta é o percentual médio do desconto dos itens de linha para clientes da região 'West' com saldo de crédito superior a $50000.

### Análise

A resposta tem alguns pontos positivos:

- Tentou corrigir o fato da consulta original não estar selecionando nada, incluindo uma tentativa de cálculo da média conforme o contexto solicitado.
- Sugeriu a criação de índices para as junções de tabelas e filtros.
- Deu explicação sobre a utilização de SUM, COUNT e ORDER BY, sugerindo como isso poded impactar na performance.

Também tem pontos negativos:

- Sugeriu a criação de índices, mas não gerou o script, não atendendo o solicitado no prompt.
- A execução da consulta não funciona, gerando o erro:

```
ERROR:  function round(double precision, integer) does not exist
LINE 2:   ROUND(SUM(l.l_discount) * 100.0 / COUNT(*), 2) AS average_...
          ^
HINT:  No function matches the given name and argument types. You might need to add explicit type casts.

ERRO:  function round(double precision, integer) does not exist
SQL state: 42883
Character: 10
```

#### Alucinações

Não parece ter alucinado, mas errou na criação da consulta.

#### Tempo de execução total da consulta (Primeira vez executando)

Não foi possível executar a consulta

#### Plano de execução

Não foi possível executar a consulta

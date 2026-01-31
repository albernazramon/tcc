# Consulta 5

## Questão

Calcule a quantidade total de peças vendidas em cada região, excluindo regiões onde o número de tipos de peças distintos é menor que 3.

## Consulta original

```sql
SELECT
  r.r_name,
  SUM(li.l_quantity)
FROM region AS r
JOIN nation AS n
  ON r.r_regionkey = n.n_regionkey
JOIN lineitem AS li
  ON li.l_partkey = n.n_nationkey
GROUP BY
  r.r_name
HAVING
  COUNT(DISTINCT li.l_partkey) >= 3;
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
  r.r_name,
  SUM(li.l_quantity)
FROM region AS r
JOIN nation AS n
  ON r.r_regionkey = n.n_regionkey
JOIN lineitem AS li
  ON li.l_partkey = n.n_nationkey
GROUP BY
  r.r_name
HAVING
  COUNT(DISTINCT li.l_partkey) >= 3;
```

**Insights:**

A consulta já está relativamente otimizada para o problema solicitado. Ela filtra as regiões com menos de 3 tipos de peças distintas usando a cláusula `HAVING`, o que é eficiente. A consulta é simples e direta, e o uso das joins é apropriado para relacionar as tabelas necessárias.

**Recomendações e Melhores Práticas:**

1.  **Índices:**
    - É altamente recomendado criar índices nas colunas utilizadas nas cláusulas `JOIN` e `WHERE`. Isso pode melhorar significativamente o desempenho da consulta, especialmente em tabelas grandes. Especificamente, considere os seguintes índices:
      - `lineitem(l_partkey, l_partkey)`: Um índice composto em `l_partkey` pode melhorar o desempenho da operação de join entre `lineitem` e `nation`.
      - `nation(n_regionkey, n_nationkey)`: Um índice em `n_regionkey` e `n_nationkey` pode otimizar o join com `region` e `lineitem`.
      - `region(r_regionkey)`: Um índice na chave primária da tabela `region` pode acelerar as operações de filtro e join.

    - Exemplo de criação de índices (comentados):

      ```sql
      CREATE INDEX idx_lineitem_partkey ON lineitem (l_partkey);
      CREATE INDEX idx_nation_regionkey ON nation (n_regionkey);
      CREATE INDEX idx_nation_nationkey ON nation (n_nationkey);
      CREATE INDEX idx_region_regionkey ON region (r_regionkey);
      ```

2.  **Análise de Desempenho:**
    - Use as ferramentas de análise de desempenho do PostgreSQL (como `EXPLAIN ANALYZE`) para identificar gargalos na consulta. Isso pode revelar se a ordem das tabelas nas cláusulas `JOIN` está otimizada ou se existem outras operações que podem ser melhoradas.
3.  **Tamanho das Tabelas:**
    - Se as tabelas forem muito grandes, considere particioná-las (por exemplo, por ano ou região) para melhorar o desempenho das consultas que acessam apenas um subconjunto dos dados.
4.  **Estatísticas:**
    - Verifique se as estatísticas das tabelas estão atualizadas. O otimizador de consultas do PostgreSQL usa essas estatísticas para escolher os planos de execução mais eficientes.
5.  **Refatoração (Menos Importante neste caso):**
    - A consulta já é relativamente simples. Não há muitas oportunidades de refatoração sem comprometer a clareza.

**Observações:**

- A consulta já cumpre o objetivo de calcular a quantidade total de peças vendidas em cada região, excluindo regiões com menos de 3 tipos de peças distintas.
- A consulta foi validada quanto à correção, compatibilidade com PostgreSQL e sentido no contexto dos schemas fornecidos.

**Resumo:**

A otimização mais importante nesta situação é a criação de índices nas colunas envolvidas nas operações de join e filtro. Além disso, o monitoramento do desempenho da consulta e a atualização das estatísticas do banco de dados podem ajudar a garantir que a consulta esteja sempre executando de forma eficiente.

#### Análise

Resposta padrão, sugerindo a criação de índices (inclusive compostos) e particionamento.

#### Alucinações

Não

#### Tempo de execução total da consulta (Primeira vez executando)

50 msec

#### Plano de execução

```
"GroupAggregate  (cost=470.62..471.80 rows=2 width=126) (actual time=0.835..0.885 rows=5.00 loops=1)"
"  Group Key: r.r_name"
"  Filter: (count(DISTINCT li.l_partkey) >= 3)"
"  Buffers: shared hit=583"
"  ->  Sort  (cost=470.62..470.90 rows=112 width=126) (actual time=0.817..0.833 rows=506.00 loops=1)"
"        Sort Key: r.r_name, li.l_partkey"
"        Sort Method: quicksort  Memory: 41kB"
"        Buffers: shared hit=583"
"        ->  Nested Loop  (cost=1.54..466.81 rows=112 width=126) (actual time=0.051..0.632 rows=506.00 loops=1)"
"              Buffers: shared hit=583"
"              ->  Hash Join  (cost=1.11..2.51 rows=5 width=122) (actual time=0.034..0.044 rows=25.00 loops=1)"
"                    Hash Cond: (n.n_regionkey = r.r_regionkey)"
"                    Buffers: shared hit=2"
"                    ->  Seq Scan on nation n  (cost=0.00..1.25 rows=25 width=8) (actual time=0.018..0.020 rows=25.00 loops=1)"
"                          Buffers: shared hit=1"
"                    ->  Hash  (cost=1.05..1.05 rows=5 width=122) (actual time=0.009..0.010 rows=5.00 loops=1)"
"                          Buckets: 1024  Batches: 1  Memory Usage: 9kB"
"                          Buffers: shared hit=1"
"                          ->  Seq Scan on region r  (cost=0.00..1.05 rows=5 width=122) (actual time=0.007..0.007 rows=5.00 loops=1)"
"                                Buffers: shared hit=1"
"              ->  Index Scan using idx_lineitem_partkey on lineitem li  (cost=0.43..92.64 rows=22 width=8) (actual time=0.002..0.021 rows=20.24 loops=25)"
"                    Index Cond: (l_partkey = n.n_nationkey)"
"                    Index Searches: 25"
"                    Buffers: shared hit=581"
"Planning Time: 0.205 ms"
"Execution Time: 0.967 ms"
```

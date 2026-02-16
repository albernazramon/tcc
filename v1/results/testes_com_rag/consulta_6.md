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
  l.l_shipdate,
  l.l_extendedprice,
  l.l_quantity,
  l.l_discount,
  o.o_orderdate,
  c.c_name,
  n.n_name AS nation_name,
  r.r_name AS region_name
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

**Insights e Explicações:**

1.  **Revisão da Consulta Original:** A consulta original era funcionalmente correta, mas podemos otimizá-la para melhor desempenho.
2.  **Explicação do Plano de Execução:** A consulta utiliza joins para relacionar as tabelas. O PostgreSQL, por padrão, escolherá um plano de execução que pode envolver a varredura completa das tabelas (full table scans) se não houver índices apropriados.
3.  **Sugestão de Índices:**
    - **Criação de Índice em `lineitem.l_orderkey`:** Um índice na coluna `l_orderkey` da tabela `lineitem` pode acelerar significativamente a junção com a tabela `orders`.
    - **Criação de Índice em `orders.o_orderkey`:** Um índice na coluna `o_orderkey` da tabela `orders` pode acelerar significativamente a junção com a tabela `lineitem`.
    - **Criação de Índice em `customer.c_custkey`:** Um índice na coluna `c_custkey` da tabela `customer` pode acelerar significativamente a junção com a tabela `orders`.
    - **Criação de Índice em `nation.n_nationkey`:** Um índice na coluna `n_nationkey` da tabela `nation` pode acelerar significativamente a junção com a tabela `customer`.
    - **Criação de Índice em `region.r_regionkey`:** Um índice na coluna `r_regionkey` da tabela `region` pode acelerar significativamente a junção com a tabela `nation`.
    - **Criação de Índice em `customer.c_acctbal`:** Um índice na coluna `c_acctbal` da tabela `customer` pode acelerar significativamente a condição de filtro.
4.  **Otimização da Expressão `WHERE`:** A expressão `WHERE` já está bem escrita e eficiente.
5.  **Ordenação:** A cláusula `ORDER BY l.l_shipdate DESC` é correta e garante que os resultados sejam retornados em ordem decrescente de data de envio.
6.  **Seleção de Colunas:** A consulta seleciona as colunas necessárias, o que ajuda a reduzir a quantidade de dados transferidos.
7.  **Alias de Tabelas:** O uso de alias de tabela (e.g., `l` para `lineitem`) torna a consulta mais legível e concisa.

**Considerações Adicionais:**

- **Estatísticas de Otimização:** Certifique-se de que o PostgreSQL tenha estatísticas atualizadas para todas as tabelas envolvidas na consulta. As estatísticas ajudam o otimizador de consultas a escolher o plano de execução mais eficiente. Você pode atualizar as estatísticas usando o comando `ANALYZE`.
- **Teste e Monitoramento:** Após criar os índices, execute a consulta e monitore o plano de execução para verificar se os índices estão sendo usados de forma eficaz. Use `EXPLAIN ANALYZE` para obter informações detalhadas sobre o plano de execução.

**Implementação dos Índices (Exemplo):**

```sql
CREATE INDEX idx_lineitem_l_orderkey ON lineitem (l_orderkey);
CREATE INDEX idx_orders_o_orderkey ON orders (o_orderkey);
CREATE INDEX idx_customer_c_custkey ON customer (c_custkey);
CREATE INDEX idx_nation_n_nationkey ON nation (n_nationkey);
CREATE INDEX idx_region_r_regionkey ON region (r_regionkey);
CREATE INDEX idx_customer_c_acctbal ON customer (c_acctbal);
```

### Análise

- O primeiro ponto é sobre a consulta devolvida. Embora a consulta original não estivesse selecionando nenhum campo, a consulta devolvida, mesmo com o contexto do que deveria buscar sendo enviado em **informações adicionais**, não contém `o percentual médio de desconto para itens de linha`, e sim alguns campos das tabelas.

#### Alucinações

A LLM retornou campos não solicitados, o que pode indicar alucinação, visto que foi enviado o contexto do que a consulta deveria fazer.

#### Tempo de execução total da consulta (Primeira vez executando)

5 secs 876 mse

Obs.: Para a consulta trazer dados, os filtros foram alterados para ` r.r_name = 'AFRICA' AND c.c_acctbal > 1000`

#### Plano de execução

```
"Gather Merge  (cost=42798.71..59674.59 rows=144899 width=289) (actual time=4010.570..4193.898 rows=858407.00 loops=1)"
"  Workers Planned: 2"
"  Workers Launched: 2"
"  Buffers: shared hit=942744 read=549533, temp read=8306 written=8328"
"  ->  Sort  (cost=41798.68..41949.62 rows=60375 width=289) (actual time=3888.991..3938.400 rows=286135.67 loops=3)"
"        Sort Key: l.l_shipdate DESC"
"        Sort Method: external merge  Disk: 23656kB"
"        Buffers: shared hit=942744 read=549533, temp read=8306 written=8328"
"        Worker 0:  Sort Method: external merge  Disk: 21416kB"
"        Worker 1:  Sort Method: external merge  Disk: 21376kB"
"        ->  Nested Loop  (cost=3.30..28747.91 rows=60375 width=289) (actual time=2.105..3127.978 rows=286135.67 loops=3)"
"              Buffers: shared hit=942730 read=549531"
"              ->  Nested Loop  (cost=2.87..8157.20 rows=20472 width=270) (actual time=1.475..1194.618 rows=97452.33 loops=3)"
"                    Buffers: shared hit=152882 read=230843"
"                    ->  Hash Join  (cost=2.44..4532.09 rows=2047 width=259) (actual time=1.103..28.175 rows=9765.33 loops=3)"
"                          Hash Cond: (c.c_nationkey = n.n_nationkey)"
"                          Buffers: shared hit=4 read=3538"
"                          ->  Parallel Seq Scan on customer c  (cost=0.00..4317.25 rows=51180 width=27) (actual time=0.286..19.050 rows=40811.67 loops=3)"
"                                Filter: (c_acctbal > '1000'::double precision)"
"                                Rows Removed by Filter: 9188"
"                                Buffers: shared read=3536"
"                          ->  Hash  (cost=2.43..2.43 rows=1 width=240) (actual time=0.808..0.812 rows=6.00 loops=3)"
"                                Buckets: 1024  Batches: 1  Memory Usage: 9kB"
"                                Buffers: shared hit=4 read=2"
"                                ->  Hash Join  (cost=1.07..2.43 rows=1 width=240) (actual time=0.797..0.805 rows=6.00 loops=3)"
"                                      Hash Cond: (n.n_regionkey = r.r_regionkey)"
"                                      Buffers: shared hit=4 read=2"
"                                      ->  Seq Scan on nation n  (cost=0.00..1.25 rows=25 width=126) (actual time=0.439..0.440 rows=25.00 loops=3)"
"                                            Buffers: shared hit=2 read=1"
"                                      ->  Hash  (cost=1.06..1.06 rows=1 width=122) (actual time=0.347..0.349 rows=1.00 loops=3)"
"                                            Buckets: 1024  Batches: 1  Memory Usage: 9kB"
"                                            Buffers: shared hit=2 read=1"
"                                            ->  Seq Scan on region r  (cost=0.00..1.06 rows=1 width=122) (actual time=0.340..0.341 rows=1.00 loops=3)"
"                                                  Filter: ((r_name)::text = 'AFRICA'::text)"
"                                                  Rows Removed by Filter: 4"
"                                                  Buffers: shared hit=2 read=1"
"                    ->  Index Scan using idx_orders_custkey on orders o  (cost=0.43..1.61 rows=16 width=19) (actual time=0.010..0.117 rows=9.98 loops=29296)"
"                          Index Cond: (o_custkey = c.c_custkey)"
"                          Index Searches: 29296"
"                          Buffers: shared hit=152878 read=227305"
"              ->  Index Scan using idx_lineitem_l_orderkey on lineitem l  (cost=0.43..0.89 rows=12 width=27) (actual time=0.018..0.019 rows=2.94 loops=292357)"
"                    Index Cond: (l_orderkey = o.o_orderkey)"
"                    Index Searches: 292357"
"                    Buffers: shared hit=789848 read=318688"
"Planning:"
"  Buffers: shared hit=15 read=17"
"Planning Time: 1.358 ms"
"Execution Time: 4222.107 ms"
```

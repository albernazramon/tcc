# Consulta 4

## Questão

Quero saber quantos clientes tenho em cada país e ordenar os resultados para exibir primeiro os países com mais clientes.

## Consulta original

```sql
SELECT
  n.n_name,
  COUNT(c.c_custkey) AS customer_count
FROM nation AS n
JOIN customer AS c
  ON n.n_nationkey = c.c_nationkey
GROUP BY
  n.n_name
ORDER BY
  customer_count DESC
LIMIT 10;
```

## Schemas

```sql
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
```

# Otimizando com a LLM

## 1. Informando apenas a consulta

#### Resposta da LLM

A consulta SQL fornecida já é relativamente otimizada para o objetivo de obter os 10 países com mais clientes. No entanto, podemos adicionar alguns insights para melhorar ainda mais o desempenho e a clareza da consulta.

**Análise da Consulta Original:**

A consulta utiliza um `JOIN` para combinar as tabelas `nation` e `customer` com base na chave estrangeira `c_nationkey`. Em seguida, agrupa os resultados por `n_name` (nome do país) e conta o número de clientes (`c_custkey`) em cada país. Finalmente, ordena os resultados em ordem decrescente de `customer_count` e limita o resultado aos 10 primeiros.

**Consulta Otimizada:**

```sql
SELECT
  n.n_name,
  COUNT(c.c_custkey) AS customer_count
FROM nation AS n
JOIN customer AS c
  ON n.n_nationkey = c.c_nationkey
GROUP BY
  n.n_name
ORDER BY
  customer_count DESC
LIMIT 10;
```

**Insights e Recomendações:**

1.  **Índices:**
    - **`customer.c_nationkey`:** Certifique-se de que existe um índice nesta coluna. Este índice é crucial para a performance da junção (`JOIN`) entre as tabelas `customer` e `nation`. Se ainda não existir, crie o seguinte:
      ```sql
      CREATE INDEX idx_customer_c_nationkey ON customer (c_nationkey);
      ```
    - **`nation.n_nationkey`:** Um índice nesta coluna também é importante, embora possa já existir como chave primária.
      ```sql
      CREATE INDEX idx_nation_n_nationkey ON nation (n_nationkey);
      ```
    - **`nation.n_name`:** Um índice nesta coluna pode acelerar a ordenação e a agregação por país.
      ```sql
      CREATE INDEX idx_nation_n_name ON nation (n_name);
      ```

2.  **Estatísticas da Tabela:** Verifique se as estatísticas das tabelas `customer` e `nation` estão atualizadas. Estatísticas precisas ajudam o otimizador de consultas a escolher o plano de execução mais eficiente. Use o comando `ANALYZE` para atualizar as estatísticas:

    ```sql
    ANALYZE customer;
    ANALYZE nation;
    ```

3.  **Análise do Plano de Execução:** Use a ferramenta `EXPLAIN ANALYZE` antes da execução da consulta para identificar gargalos de desempenho. Isso permitirá que você veja como o PostgreSQL está executando a consulta e onde pode haver oportunidades de otimização. Exemplo:

    ```sql
    EXPLAIN ANALYZE SELECT
      n.n_name,
      COUNT(c.c_custkey) AS customer_count
    FROM nation AS n
    JOIN customer AS c
      ON n.n_nationkey = c.c_nationkey
    GROUP BY
      n.n_name
    ORDER BY
      customer_count DESC
    LIMIT 10;
    ```

4.  **Considerações Adicionais:**
    - **Volume de Dados:** Se as tabelas `customer` e `nation` forem muito grandes, considere particionar as tabelas por país ou região para melhorar o desempenho das consultas.
    - **Hardware:** O desempenho da consulta também pode ser afetado pelo hardware do servidor de banco de dados (CPU, memória, disco).

**Observação:** A consulta original já está bem estruturada. As melhorias sugeridas são focadas em garantir que o PostgreSQL tenha as informações necessárias para otimizar a execução da consulta de forma eficaz.

Espero que estas sugestões sejam úteis!

### Análise

#### Alucinações

Não

#### Tempo de execução total da consulta (Primeira vez executando)

106 msec

#### Plano de execução

```
"Limit  (cost=6325.37..6325.39 rows=10 width=126) (actual time=84.673..89.461 rows=10.00 loops=1)"
"  Buffers: shared hit=18 read=3519"
"  ->  Sort  (cost=6325.37..6325.43 rows=25 width=126) (actual time=84.672..89.459 rows=10.00 loops=1)"
"        Sort Key: (count(c.c_custkey)) DESC"
"        Sort Method: top-N heapsort  Memory: 25kB"
"        Buffers: shared hit=18 read=3519"
"        ->  Finalize GroupAggregate  (cost=6317.29..6324.83 rows=25 width=126) (actual time=84.620..89.447 rows=25.00 loops=1)"
"              Group Key: n.n_name"
"              Buffers: shared hit=18 read=3519"
"              ->  Gather Merge  (cost=6317.29..6324.28 rows=60 width=126) (actual time=84.613..89.420 rows=75.00 loops=1)"
"                    Workers Planned: 2"
"                    Workers Launched: 2"
"                    Buffers: shared hit=18 read=3519"
"                    ->  Sort  (cost=5317.27..5317.33 rows=25 width=126) (actual time=43.477..43.479 rows=25.00 loops=3)"
"                          Sort Key: n.n_name"
"                          Sort Method: quicksort  Memory: 25kB"
"                          Buffers: shared hit=18 read=3519"
"                          Worker 0:  Sort Method: quicksort  Memory: 25kB"
"                          Worker 1:  Sort Method: quicksort  Memory: 25kB"
"                          ->  Partial HashAggregate  (cost=5316.44..5316.69 rows=25 width=126) (actual time=43.400..43.404 rows=25.00 loops=3)"
"                                Group Key: n.n_name"
"                                Batches: 1  Memory Usage: 32kB"
"                                Buffers: shared hit=3 read=3518"
"                                Worker 0:  Batches: 1  Memory Usage: 32kB"
"                                Worker 1:  Batches: 1  Memory Usage: 32kB"
"                                ->  Hash Join  (cost=1.56..5003.94 rows=62500 width=122) (actual time=1.422..33.833 rows=50000.00 loops=3)"
"                                      Hash Cond: (c.c_nationkey = n.n_nationkey)"
"                                      Buffers: shared hit=3 read=3518"
"                                      ->  Parallel Seq Scan on customer c  (cost=0.00..4143.00 rows=62500 width=8) (actual time=1.130..22.379 rows=50000.00 loops=3)"
"                                            Buffers: shared read=3518"
"                                      ->  Hash  (cost=1.25..1.25 rows=25 width=122) (actual time=0.279..0.280 rows=25.00 loops=3)"
"                                            Buckets: 1024  Batches: 1  Memory Usage: 10kB"
"                                            Buffers: shared hit=3"
"                                            ->  Seq Scan on nation n  (cost=0.00..1.25 rows=25 width=122) (actual time=0.265..0.268 rows=25.00 loops=3)"
"                                                  Buffers: shared hit=3"
"Planning:"
"  Buffers: shared hit=16 read=3 dirtied=2"
"Planning Time: 1.560 ms"
"Execution Time: 89.530 ms"
```

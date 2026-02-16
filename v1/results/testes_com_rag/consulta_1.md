# Consulta 1

## Questão

Quero saber quantos clientes tenho em cada país e ordenar os resultados para exibir primeiro os países com mais clientes.

## Consulta original

```sql
SELECT
  n.n_name,
  COUNT(c.c_custkey) AS num_customers
FROM nation AS n
JOIN customer AS c
  ON n.n_nationkey = c.c_nationkey
GROUP BY
  n.n_name
ORDER BY
  num_customers DESC;
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

#### Resposta da LLM

```sql
SELECT
  n.n_name,
  COUNT(c.c_custkey) AS num_customers
FROM nation AS n
JOIN customer AS c
  ON n.n_nationkey = c.c_nationkey
GROUP BY
  n.n_name
ORDER BY
  num_customers DESC;
```

**Insights e Recomendações:**

1.  **Índices:** A consulta já utiliza uma junção (JOIN) entre as tabelas `nation` e `customer` através da chave estrangeira `c_nationkey` e `n_nationkey`. Para otimizar o desempenho, especialmente em tabelas grandes, é altamente recomendável criar índices nas colunas usadas na junção e na cláusula `GROUP BY`. Isso acelera significativamente o processo de busca e agrupamento dos dados.

    ```sql
    CREATE INDEX idx_customer_nationkey ON customer (c_nationkey);
    CREATE INDEX idx_nation_nationkey ON nation (n_nationkey);
    ```

2.  **Estatísticas:** Certifique-se de que as estatísticas das tabelas `nation` e `customer` estejam atualizadas. O otimizador de consultas do PostgreSQL usa essas estatísticas para escolher o melhor plano de execução. Execute `ANALYZE nation` e `ANALYZE customer` periodicamente para manter as estatísticas precisas.

3.  **Cardinalidade:** Entenda a cardinalidade das colunas envolvidas na junção. Se a cardinalidade de `c_nationkey` for alta (muitos clientes por país), o otimizador provavelmente escolherá um plano de execução eficiente. No entanto, se a cardinalidade for baixa (poucos clientes por país), o otimizador pode ter mais dificuldade em escolher o melhor plano.

4.  **Cláusula `ORDER BY`:** A cláusula `ORDER BY num_customers DESC` é essencial para retornar os resultados na ordem solicitada (países com mais clientes primeiro). O otimizador pode aproveitar os índices criados para otimizar a ordenação.

5.  **Genetic Query Optimizer (Gequo):** Para consultas complexas que envolvem muitas junções e/ou grandes volumes de dados, o Genetic Query Optimizer (GEQO) pode ser ativado. A configuração `jit_inline_above_cost` pode ser ajustada, mas normalmente o PostgreSQL lida bem com as junções nesta consulta.
    A chave é que o otimizador é inteligente e pode escolher entre diversos planos de execução. O `EXPLAIN` (descrito na documentação do PostgreSQL) é uma ferramenta crucial para entender o plano escolhido e verificar se ele está utilizando os índices corretamente.

6.  **Revisão do Plano de Execução:** Use o comando `EXPLAIN ANALYZE` antes e depois de criar os índices. Isso fornecerá informações detalhadas sobre o plano de execução da consulta e os tempos reais gastos em cada etapa. Analise o resultado para identificar gargalos de desempenho e ajustar sua estratégia de otimização.

    ```sql
    EXPLAIN ANALYZE SELECT
      n.n_name,
      COUNT(c.c_custkey) AS num_customers
    FROM nation AS n
    JOIN customer AS c
      ON n.n_nationkey = c.c_nationkey
    GROUP BY
      n.n_name
    ORDER BY
      num_customers DESC;
    ```

7.  **Considerações sobre o `DISTINCT`:** Se a consulta for executada em um ambiente com dados muito duplicados, a operação `COUNT(c.c_custkey)` pode ser lenta.

**Resumo:**

A consulta já é relativamente simples e bem escrita. As principais otimizações focam na criação de índices apropriados e na garantia de que as estatísticas da tabela estejam atualizadas. Além disso, monitorar o plano de execução da consulta com `EXPLAIN ANALYZE` é fundamental para identificar oportunidades adicionais de otimização e validar as mudanças feitas.

#### Análise

Com a inserção do RAG a LLM trouxe alguns pontos positivos/negativos se comparado apenas com o prompt:

- Positivos:
  - Manteve a indicação da criação de índices, nas mesmas colunas.
  - Explicou sobre cardinalidade entre as tabelas, falando sobre como a quantidade de registros pode impactar na relação.
  - Falou sobre o GEQUO para tabelas com muitos JOINs ou grandes volumes de dados.
  - Explicou que consultas com muitos dados duplicados pode ficar muito lenta na utilização de COUNT.
- Negativos:
  - Falou que o JOIN entre as tabelas já utiliza FK, porém ao olhar o schema, não existe uma chave estrangeira entre as tabelas.
  - Respondeu com um tópico sobre o DISTINCT, mas no texto falava de COUNT, não deixando claro se no caso proposto (muitos dados duplicados) deveria ser utilizado o DISTINCT.

#### Alucinações

A única alucinação foi falar que as tabelas possuem chave estrangeira.

#### Tempo de execução total da consulta (Primeira vez executando)

229 msec

#### Plano de execução

```
"Sort  (cost=6343.41..6343.47 rows=25 width=126) (actual time=66.905..71.773 rows=25.00 loops=1)"
"  Sort Key: (count(c.c_custkey)) DESC"
"  Sort Method: quicksort  Memory: 25kB"
"  Buffers: shared hit=3555"
"  ->  Finalize GroupAggregate  (cost=6335.29..6342.83 rows=25 width=126) (actual time=66.857..71.761 rows=25.00 loops=1)"
"        Group Key: n.n_name"
"        Buffers: shared hit=3555"
"        ->  Gather Merge  (cost=6335.29..6342.28 rows=60 width=126) (actual time=66.851..71.742 rows=75.00 loops=1)"
"              Workers Planned: 2"
"              Workers Launched: 2"
"              Buffers: shared hit=3555"
"              ->  Sort  (cost=5335.27..5335.33 rows=25 width=126) (actual time=26.856..26.858 rows=25.00 loops=3)"
"                    Sort Key: n.n_name"
"                    Sort Method: quicksort  Memory: 25kB"
"                    Buffers: shared hit=3555"
"                    Worker 0:  Sort Method: quicksort  Memory: 25kB"
"                    Worker 1:  Sort Method: quicksort  Memory: 25kB"
"                    ->  Partial HashAggregate  (cost=5334.44..5334.69 rows=25 width=126) (actual time=26.797..26.801 rows=25.00 loops=3)"
"                          Group Key: n.n_name"
"                          Batches: 1  Memory Usage: 32kB"
"                          Buffers: shared hit=3539"
"                          Worker 0:  Batches: 1  Memory Usage: 32kB"
"                          Worker 1:  Batches: 1  Memory Usage: 32kB"
"                          ->  Hash Join  (cost=1.56..5021.94 rows=62500 width=122) (actual time=0.242..17.268 rows=50000.00 loops=3)"
"                                Hash Cond: (c.c_nationkey = n.n_nationkey)"
"                                Buffers: shared hit=3539"
"                                ->  Parallel Seq Scan on customer c  (cost=0.00..4161.00 rows=62500 width=8) (actual time=0.009..3.612 rows=50000.00 loops=3)"
"                                      Buffers: shared hit=3536"
"                                ->  Hash  (cost=1.25..1.25 rows=25 width=122) (actual time=0.223..0.223 rows=25.00 loops=3)"
"                                      Buckets: 1024  Batches: 1  Memory Usage: 10kB"
"                                      Buffers: shared hit=3"
"                                      ->  Seq Scan on nation n  (cost=0.00..1.25 rows=25 width=122) (actual time=0.209..0.212 rows=25.00 loops=3)"
"                                            Buffers: shared hit=3"
"Planning Time: 0.395 ms"
"Execution Time: 71.885 ms"
```

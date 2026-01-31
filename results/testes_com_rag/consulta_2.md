# Consulta 2

## Questão

Quais são os 5 principais clientes com o maior valor total de pedidos?

## Consulta original

```sql
SELECT c.c_name
FROM customer c
JOIN orders o ON c.c_custkey = o.o_custkey
GROUP BY c.c_custkey
ORDER BY SUM(o.o_totalprice) DESC
LIMIT 5;
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

CREATE TABLE IF NOT EXISTS public.orders
(
    o_orderdate character varying(50) COLLATE pg_catalog."default",
    o_orderkey integer,
    o_custkey integer,
    o_orderpriority character varying(50) COLLATE pg_catalog."default",
    o_shippriority integer,
    o_clerk character varying(50) COLLATE pg_catalog."default",
    o_orderstatus character varying(50) COLLATE pg_catalog."default",
    o_totalprice real,
    o_comment character varying(128) COLLATE pg_catalog."default"
)
```

# Otimizando com a LLM

#### Resposta da LLM

```sql
SELECT c.c_name
FROM customer c
JOIN orders o ON c.c_custkey = o.o_custkey
GROUP BY c.c_custkey
ORDER BY SUM(o.o_totalprice) DESC
LIMIT 5;
```

**Insights e Recomendações de Otimização:**

1. **Índices:** A consulta atualmente não utiliza índices, o que pode levar a uma varredura completa das tabelas `customer` e `orders`. A criação de índices nas colunas envolvidas nas junções e na função de agregação é crucial para melhorar o desempenho.
   - **Índice em `customer.c_custkey`:** Fundamental para a junção com a tabela `orders`.
   - **Índice em `orders.o_custkey`:** Fundamental para a junção com a tabela `customer`.
   - **Índice em `orders.o_totalprice`:** Essencial para a função de agregação `SUM()`.
   - **Índice composto em `(c_custkey, o_totalprice)`:** É a otimização mais relevante, pois combina as necessidades das junções e da agregação. PostgreSQL pode usar esse índice para satisfazer ambas as condições na mesma operação.

   ```sql
   CREATE INDEX idx_customer_custkey ON customer (c_custkey);
   CREATE INDEX idx_orders_custkey ON orders (o_custkey);
   CREATE INDEX idx_orders_totalprice ON orders (o_totalprice);
   CREATE INDEX idx_customer_orders ON customer (c_custkey, o_totalprice);
   ```

2. **Análise de Dados:** Certifique-se de que as estatísticas das tabelas `customer` e `orders` estejam atualizadas. O otimizador de consulta usa essas estatísticas para escolher o melhor plano de execução. Execute `ANALYZE customer` e `ANALYZE orders` periodicamente, especialmente após alterações significativas nos dados.

3. **Genetic Query Optimizer (Gequo):** Se o número de joins for grande (mais de 2-3), o PostgreSQL utiliza o Genetic Query Optimizer (GEQO). Se a consulta for complexa e envolver muitas junções, o GEQO pode ajudar a encontrar um plano de execução melhor, mas pode ser mais lento que o otimizador normal do PostgreSQL. Para otimizar o GEQO, você pode ajustar o parâmetro `jit_inline_above_cost`. Um valor de -1 desabilita as otimizações caras.

4. **EXPLAIN:** Utilize o comando `EXPLAIN` para analisar o plano de execução da consulta após a criação dos índices. Isso permitirá que você verifique se os índices estão sendo utilizados e se o plano de execução é o desejado.

5. **Tamanho dos Dados:** O desempenho também depende do tamanho das tabelas `customer` e `orders`. Para tabelas muito grandes, considere particionar as tabelas em partes menores para melhorar o desempenho das consultas.

6. **`LIMIT`:** A cláusula `LIMIT 5` é eficiente e não deve impactar significativamente o desempenho, já que é usada para retornar apenas os 5 principais clientes.

7. **Considerações sobre o Tipo de Dados:** Garanta que os tipos de dados nas colunas de junção (`c_custkey` e `o_custkey`) sejam exatamente iguais para otimizar a comparação e o uso de índices.

**Observações:**

- A ordem dos índices é importante. O índice composto `idx_customer_orders` é projetado especificamente para otimizar esta consulta.
- A criação de índices tem um custo, pois ocupa espaço em disco e pode tornar as operações de inserção, atualização e exclusão mais lentas. Avalie cuidadosamente o impacto da criação de índices antes de implementá-los.
- Após a criação dos índices, execute a consulta novamente e verifique se o plano de execução indica que os índices estão sendo usados. Utilize `EXPLAIN` para análise.

#### Análise

Assim como no cenário 1, a LLM manteve alguns comportamentos como indicar a criação de índices nas tabelas, utilização do ANALYZE e EXPLAIN para atualização de estatísticas e plano de execução da consulta. Também falou sobre o uso de Gequo para consultas que contém muitos joins.

Diferente do cenário 1, essa resposta não conteve a indicação da existência de FKs.

A LLM errou na criação de índices, gerando um script para a criação de índice composto na tabela `customer`, indicando a existência de um campo `o_totalprice`, sendo que esse campo está presente na tabela `orders`.

Outro ponto negativo: DIferente do teste apenas com o prompt, no cenário atual a LLM não falou nada sobre a coluna faltante no GROUP BY. Sem isso, a consulta original não funciona.

#### Alucinações

A única alucinação percebida foi o erro na indicação de índice com coluna inexistente na tabela indica, porém presente em outra tabela utilizada na consulta.

#### Tempo de execução total da consulta (Primeira vez executando)

680 msec

**Observação: ** A consulta foi executada com uma correção manual do GROUP BY e sem o índice incorreto indicado pela LLM.

#### Plano de execução

```
"Limit  (cost=169858.63..169858.65 rows=5 width=27) (actual time=701.152..709.040 rows=5.00 loops=1)"
"  Buffers: shared hit=6904 read=22862, temp read=1387 written=1390"
"  ->  Sort  (cost=169858.63..170233.63 rows=150000 width=27) (actual time=701.151..709.038 rows=5.00 loops=1)"
"        Sort Key: (sum(o.o_totalprice)) DESC"
"        Sort Method: top-N heapsort  Memory: 25kB"
"        Buffers: shared hit=6904 read=22862, temp read=1387 written=1390"
"        ->  Finalize GroupAggregate  (cost=121239.26..167367.19 rows=150000 width=27) (actual time=601.509..698.214 rows=100000.00 loops=1)"
"              Group Key: c.c_custkey, c.c_name"
"              Buffers: shared hit=6904 read=22862, temp read=1387 written=1390"
"              ->  Gather Merge  (cost=121239.26..163167.19 rows=360000 width=27) (actual time=601.498..653.454 rows=297947.00 loops=1)"
"                    Workers Planned: 2"
"                    Workers Launched: 2"
"                    Buffers: shared hit=6904 read=22862, temp read=1387 written=1390"
"                    ->  Sort  (cost=120239.23..120614.23 rows=150000 width=27) (actual time=560.344..570.321 rows=99315.67 loops=3)"
"                          Sort Key: c.c_custkey, c.c_name"
"                          Sort Method: external merge  Disk: 3704kB"
"                          Buffers: shared hit=6904 read=22862, temp read=1387 written=1390"
"                          Worker 0:  Sort Method: external merge  Disk: 3696kB"
"                          Worker 1:  Sort Method: external merge  Disk: 3696kB"
"                          ->  Partial HashAggregate  (cost=93707.36..103752.28 rows=150000 width=27) (actual time=505.863..526.208 rows=99315.67 loops=3)"
"                                Group Key: c.c_custkey, c.c_name"
"                                Planned Partitions: 4  Batches: 1  Memory Usage: 7705kB"
"                                Buffers: shared hit=6874 read=22862"
"                                Worker 0:  Batches: 1  Memory Usage: 7705kB"
"                                Worker 1:  Batches: 1  Memory Usage: 7705kB"
"                                ->  Parallel Hash Join  (cost=4942.25..42340.17 rows=625000 width=27) (actual time=16.441..302.147 rows=500000.00 loops=3)"
"                                      Hash Cond: (o.o_custkey = c.c_custkey)"
"                                      Buffers: shared hit=6874 read=22862"
"                                      ->  Parallel Seq Scan on orders o  (cost=0.00..32450.00 rows=625000 width=8) (actual time=0.296..37.741 rows=500000.00 loops=3)"
"                                            Buffers: shared hit=3338 read=22862"
"                                      ->  Parallel Hash  (cost=4161.00..4161.00 rows=62500 width=23) (actual time=15.821..15.821 rows=50000.00 loops=3)"
"                                            Buckets: 262144  Batches: 1  Memory Usage: 10272kB"
"                                            Buffers: shared hit=3536"
"                                            ->  Parallel Seq Scan on customer c  (cost=0.00..4161.00 rows=62500 width=23) (actual time=0.007..18.772 rows=150000.00 loops=1)"
"                                                  Buffers: shared hit=3536"
"Planning:"
"  Buffers: shared hit=16"
"Planning Time: 0.541 ms"
"Execution Time: 710.980 ms"
```

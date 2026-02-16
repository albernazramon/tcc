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

A consulta SQL fornecida já está relativamente otimizada para o problema solicitado. Ela busca os 5 clientes com o maior valor total de pedidos, utilizando `GROUP BY` e `ORDER BY` para realizar essa tarefa. No entanto, podemos fazer algumas otimizações e adicionar insights para melhorar o desempenho e a clareza da consulta.

**Consulta Otimizada:**

```sql
SELECT
  c.c_name,
  SUM(o.o_totalprice) AS total_order_value
FROM customer c
JOIN orders o
  ON c.c_custkey = o.o_custkey
GROUP BY
  c.c_custkey,
  c.c_name  -- Incluir c_name no GROUP BY é importante para garantir a correta agregação
ORDER BY
  total_order_value DESC
LIMIT 5;
```

**Insights e Melhorias:**

1.  **Clareza e Legibilidade:** Adicionei o alias `total_order_value` para a coluna agregada, tornando o resultado mais fácil de entender.
2.  **GROUP BY:** Incluí `c.c_name` no `GROUP BY`. É uma boa prática e, em alguns casos, pode ser necessário para garantir que a agregação seja feita corretamente, especialmente se houver múltiplas linhas com o mesmo `c_custkey`. Embora o PostgreSQL possa permitir a omissão, incluir explicitamente garante o comportamento esperado em todos os ambientes.
3.  **Índices:**
    - **Crie um índice na coluna `customer.c_custkey`:** Este índice acelerará a busca na tabela `customer` com base na chave estrangeira `o_custkey` na tabela `orders`.
    - **Crie um índice na coluna `orders.o_custkey`:** Este índice acelerará a busca na tabela `orders` com base na chave estrangeira `c_custkey` na tabela `customer`.
    - **Crie um índice na coluna `orders.o_totalprice`:** Este índice acelerará a ordenação pela coluna `o_totalprice`.
    - **Considerar um índice composto em `customer(c_custkey, c_name)`:** Se as consultas forem frequentemente filtradas ou ordenadas por `c_custkey` e `c_name`, um índice composto pode melhorar o desempenho.

    ```sql
    -- Script DDL para criar os índices
    CREATE INDEX idx_customer_custkey ON customer (c_custkey);
    CREATE INDEX idx_orders_custkey ON orders (o_custkey);
    CREATE INDEX idx_orders_totalprice ON orders (o_totalprice);
    CREATE INDEX idx_customer_cname_custkey ON customer (c_name, c_custkey); -- Índice composto
    ```

4.  **Otimização da Consulta:** A consulta é eficiente para o problema proposto. A ordenação final (`ORDER BY total_order_value DESC`) e o uso do `LIMIT` são adequados para obter os 5 principais clientes.
5.  **Considerações Adicionais:**
    - **Volume de Dados:** Se as tabelas `customer` e `orders` forem muito grandes, considere particionar as tabelas em intervalos de tempo ou por outros critérios relevantes para melhorar o desempenho das consultas.
    - **Estatísticas:** Certifique-se de que as estatísticas do banco de dados estejam atualizadas. O PostgreSQL usa estatísticas para otimizar o plano de execução das consultas. Você pode atualizar as estatísticas com o comando `ANALYZE`.
    - **Hardware:** Se o desempenho ainda for um problema, considere aumentar a capacidade de hardware do servidor de banco de dados (CPU, memória, disco).

**Em resumo:**

A consulta já está bem estruturada, mas a adição de índices e a consideração de estatísticas e particionamento (especialmente para grandes volumes de dados) podem proporcionar melhorias significativas no desempenho. Incluir o `c_name` no `GROUP BY` garante a correta agregação dos dados.

#### Análise

A resposta contém os seguintes pontos positivos:

- Indicou o uso de alias para tornar a consulta mais clara.
- Sugeriu a criação de diferentes índices, incluindo índices compostos.
- Corrigiu o GROUP BY incluindo a coluna faltante.

Pontos negativos:

- Alterou a consulta para trazer uma coluna a mais, sendo essa o valor total de pedidos. Embora isso possa ser útil, um dos critérios do prompt é o de não alterar o resultado final.

#### Alucinações

Não parece ter alucinado.

#### Tempo de execução total da consulta (Primeira vez executando)

5 secs 61 msec

#### Plano de execução

```
"Limit  (cost=160248.41..160248.42 rows=5 width=27) (actual time=5135.497..5139.505 rows=5.00 loops=1)"
"  Buffers: shared hit=1369916 read=580443"
"  ->  Sort  (cost=160248.41..160623.41 rows=150000 width=27) (actual time=5135.496..5139.503 rows=5.00 loops=1)"
"        Sort Key: (sum(o.o_totalprice)) DESC"
"        Sort Method: top-N heapsort  Memory: 25kB"
"        Buffers: shared hit=1369916 read=580443"
"        ->  Finalize GroupAggregate  (cost=1000.87..157756.96 rows=150000 width=27) (actual time=205.343..5118.774 rows=100000.00 loops=1)"
"              Group Key: c.c_name, c.c_custkey"
"              Buffers: shared hit=1369916 read=580443"
"              ->  Gather Merge  (cost=1000.87..153556.96 rows=360000 width=27) (actual time=205.184..5080.783 rows=100000.00 loops=1)"
"                    Workers Planned: 2"
"                    Workers Launched: 2"
"                    Buffers: shared hit=1369916 read=580443"
"                    ->  Partial GroupAggregate  (cost=0.85..111004.00 rows=150000 width=27) (actual time=1.176..3896.530 rows=33333.33 loops=3)"
"                          Group Key: c.c_name, c.c_custkey"
"                          Buffers: shared hit=1369916 read=580443"
"                          ->  Nested Loop  (cost=0.85..104816.50 rows=625000 width=27) (actual time=0.797..3772.588 rows=500000.00 loops=3)"
"                                Buffers: shared hit=1369916 read=580443"
"                                ->  Parallel Index Only Scan using idx_customer_cname_custkey on customer c  (cost=0.42..4359.42 rows=62500 width=23) (actual time=0.516..18.762 rows=50000.00 loops=3)"
"                                      Heap Fetches: 0"
"                                      Index Searches: 1"
"                                      Buffers: shared hit=3 read=741"
"                                ->  Index Scan using idx_orders_custkey on orders o  (cost=0.43..1.45 rows=16 width=8) (actual time=0.007..0.073 rows=10.00 loops=150000)"
"                                      Index Cond: (o_custkey = c.c_custkey)"
"                                      Index Searches: 150000"
"                                      Buffers: shared hit=1369913 read=579702"
"Planning:"
"  Buffers: shared hit=8 read=8"
"Planning Time: 0.478 ms"
"Execution Time: 5139.565 ms"
```

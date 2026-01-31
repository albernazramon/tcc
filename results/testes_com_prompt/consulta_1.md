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

## Esquemas

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

A consulta SQL fornecida já é relativamente otimizada para a tarefa solicitada. Ela usa JOINs e GROUP BY de forma eficiente para responder à pergunta sobre o número de clientes por país, e a cláusula ORDER BY garante que os resultados sejam exibidos do maior para o menor número de clientes. No entanto, podemos realizar algumas melhorias adicionais, principalmente em relação à criação de índices, que podem acelerar significativamente as operações de busca e agrupamento.

**Validação:**

1.  **Correção da Consulta:** A consulta é sintaticamente correta e pode ser executada no PostgreSQL.
2.  **Compatibilidade com PostgreSQL:** A consulta é totalmente compatível com o PostgreSQL.
3.  **Contexto dos Schemas:** A consulta faz sentido considerando os schemas fornecidos, que descrevem tabelas de países e clientes.
4.  **Informações:** As informações fornecidas (a necessidade de ordenar os países por número de clientes) são relevantes para a otimização da consulta.

**Consulta Otimizada:**

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

1.  **Criação de Índices:** A otimização mais importante nesta situação é a criação de índices nas colunas usadas nas cláusulas `JOIN` e `GROUP BY`. Especificamente, precisamos de um índice em `nation.n_nationkey` e `customer.c_nationkey`.
2.  **Índices:**

    ```sql
    CREATE INDEX idx_customer_nationkey ON customer (c_nationkey);
    CREATE INDEX idx_nation_nationkey ON nation (n_nationkey);
    ```

    Esses índices permitirão que o PostgreSQL localize rapidamente as linhas correspondentes nas tabelas `customer` e `nation` durante as operações de `JOIN` e `GROUP BY`.

3.  **Estatísticas:** Certifique-se de que as estatísticas das tabelas `nation` e `customer` estejam atualizadas. Estatísticas precisas ajudam o otimizador de consultas a escolher o melhor plano de execução. Você pode atualizar estatísticas com o comando `ANALYZE`.

    ```sql
    ANALYZE nation;
    ANALYZE customer;
    ```

4.  **Considerações Adicionais:**
    - **Volume de Dados:** Se as tabelas `nation` e `customer` contiverem um grande número de linhas, a criação de índices se torna ainda mais crucial para o desempenho.
    - **Padrões de Consulta:** Se você frequentemente executar consultas semelhantes, considere criar uma view que encapsule esta consulta otimizada. Isso pode simplificar o acesso aos dados e ainda fornecer os benefícios da otimização.
    - **Particionamento:** Se a tabela `customer` for muito grande, você pode considerar o particionamento da tabela, agrupando-a por `c_nationkey` ou outro critério relevante. Isso pode melhorar o desempenho das consultas que filtram por país.

5.  **Otimização de Hardware:** Em última análise, o desempenho da consulta também pode ser afetado pela capacidade do hardware do servidor de banco de dados. Certifique-se de que o servidor tenha recursos suficientes (CPU, memória, disco) para lidar com a carga de trabalho do banco de dados.

**Observações:**

A consulta original já está bem estruturada, mas a criação de índices é a principal recomendação para otimizar o desempenho desta consulta, especialmente se as tabelas `nation` e `customer` forem grandes. Adicionalmente, manter as estatísticas atualizadas é importante para garantir que o otimizador de consultas tome as melhores decisões.

#### Análise

A resposta foi bem completa, dando diversos insights sobre como melhorar a consulta.
Um dos principais pontos foi a sugestão de criação de índices, fornecendo o script de criação de índice.

Também é válido falar que a LLM retornou a mesma consulta da entrada, considerando-a otimizada.

#### Alucinações

Não parece ter alucinado.

#### Tempo de execução total da consulta (primeira execução)

281 msec

#### Plano de execução

```
"Sort  (cost=6325.41..6325.47 rows=25 width=126) (actual time=61.756..64.958 rows=25.00 loops=1)"
"  Sort Key: (count(c.c_custkey)) DESC"
"  Sort Method: quicksort  Memory: 25kB"
"  Buffers: shared hit=3536"
"  ->  Finalize GroupAggregate  (cost=6317.29..6324.83 rows=25 width=126) (actual time=61.730..64.949 rows=25.00 loops=1)"
"        Group Key: n.n_name"
"        Buffers: shared hit=3536"
"        ->  Gather Merge  (cost=6317.29..6324.28 rows=60 width=126) (actual time=61.721..64.934 rows=50.00 loops=1)"
"              Workers Planned: 2"
"              Workers Launched: 2"
"              Buffers: shared hit=3536"
"              ->  Sort  (cost=5317.27..5317.33 rows=25 width=126) (actual time=23.602..23.604 rows=16.67 loops=3)"
"                    Sort Key: n.n_name"
"                    Sort Method: quicksort  Memory: 25kB"
"                    Buffers: shared hit=3536"
"                    Worker 0:  Sort Method: quicksort  Memory: 25kB"
"                    Worker 1:  Sort Method: quicksort  Memory: 25kB"
"                    ->  Partial HashAggregate  (cost=5316.44..5316.69 rows=25 width=126) (actual time=23.562..23.565 rows=16.67 loops=3)"
"                          Group Key: n.n_name"
"                          Batches: 1  Memory Usage: 32kB"
"                          Buffers: shared hit=3520"
"                          Worker 0:  Batches: 1  Memory Usage: 32kB"
"                          Worker 1:  Batches: 1  Memory Usage: 32kB"
"                          ->  Hash Join  (cost=1.56..5003.94 rows=62500 width=122) (actual time=0.122..14.862 rows=50000.00 loops=3)"
"                                Hash Cond: (c.c_nationkey = n.n_nationkey)"
"                                Buffers: shared hit=3520"
"                                ->  Parallel Seq Scan on customer c  (cost=0.00..4143.00 rows=62500 width=8) (actual time=0.007..3.059 rows=50000.00 loops=3)"
"                                      Buffers: shared hit=3518"
"                                ->  Hash  (cost=1.25..1.25 rows=25 width=122) (actual time=0.158..0.158 rows=25.00 loops=2)"
"                                      Buckets: 1024  Batches: 1  Memory Usage: 10kB"
"                                      Buffers: shared hit=2"
"                                      ->  Seq Scan on nation n  (cost=0.00..1.25 rows=25 width=122) (actual time=0.144..0.147 rows=25.00 loops=2)"
"                                            Buffers: shared hit=2"
"Planning Time: 0.138 ms"
"Execution Time: 65.005 ms"
```

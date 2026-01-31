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

**Insights e Otimizações:**

1.  **Explicação da Otimização:** A consulta já está relativamente otimizada para o cenário dado. Ela realiza um JOIN entre as tabelas `nation` e `customer` para associar clientes a seus respectivos países, e então agrupa os resultados pelo nome do país (`n.n_name`) para contar o número de clientes em cada um. Finalmente, ordena os países em ordem decrescente de número de clientes e limita o resultado aos 10 primeiros.

2.  **Índices:** A otimização mais significativa que pode ser feita é a criação de um índice na coluna `n_nationkey` da tabela `nation` e na coluna `c_nationkey` da tabela `customer`. Este índice facilitará a operação `JOIN` entre as tabelas, reduzindo o tempo de execução. A criação do índice é fundamental para otimizar a consulta, especialmente em tabelas grandes.

    ```sql
    CREATE INDEX idx_nation_n_nationkey ON nation (n_nationkey);
    CREATE INDEX idx_customer_c_nationkey ON customer (c_nationkey);
    ```

3.  **Análise de Dados:** É recomendável que o usuário execute o comando `ANALYZE` na tabela `customer` e na tabela `nation` após a criação dos índices. Isso atualizará as estatísticas do otimizador de consultas, permitindo que ele escolha o plano de execução mais eficiente.

    ```sql
    ANALYZE customer;
    ANALYZE nation;
    ```

4.  **Considerações sobre o Otimizador:** O PostgreSQL possui um otimizador de consultas robusto. Em muitos casos, o otimizador será capaz de escolher um plano de execução ótimo sem intervenção manual. No entanto, a criação de índices, conforme mencionado acima, geralmente acelera significativamente a consulta, especialmente em tabelas grandes.

5.  **Genetic Query Optimizer (Gequo):** Para queries com muitas joins, o Genetic Query Optimizer (GEQO) pode ser usado. A consulta dada tem apenas um join, então o GEQO não se aplica.

6.  **Paralelismo:** Se o ambiente PostgreSQL permitir e a carga de trabalho não for crítica, considere habilitar o paralelismo para a consulta. Isso pode ser feito configurando parâmetros como `max_worker_processes` e `parallel_setup_cost`. No entanto, o paralelismo adiciona complexidade e pode não ser benéfico para queries simples como esta.

7.  **Performance Insights:**
    - **Volume de Dados:** A performance da consulta dependerá do volume de dados nas tabelas `nation` e `customer`. Em tabelas muito grandes, a criação de índices e o uso do otimizador de consultas são ainda mais importantes.
    - **Distribuição dos Dados:** A distribuição dos dados nas tabelas também pode afetar o desempenho da consulta. Se os dados estiverem altamente concentrados em algumas linhas, a consulta pode ser mais lenta.
    - **Hardware:** A performance da consulta também depende do hardware do servidor PostgreSQL (CPU, memória, disco).

8.  **Limit 10:** O `LIMIT 10` é importante para garantir que apenas os 10 países com mais clientes sejam retornados.

Espero que essas informações sejam úteis!

### Análise

Foi uma resposta padrão com a criação de índices.
Citou sobre o Otimizador do Postgre e o GEQUO novamente.
Também indicou o uso de paralelismo, explicando como habilitar. Mas informou que poderia não funcionar para esse caso e que adicionaria complexidade. Além disso não indicou se faz sentido o uso, já que a consulta usa apenas um COUNT e em outro cenário ele indicou que para o uso de COUNT não teria impacto a utilização do paralelismo.

#### Alucinações

Não parece ter alucinado.

#### Tempo de execução total da consulta (Primeira vez executando)

182 msec

#### Plano de execução

```
"Limit  (cost=6343.37..6343.39 rows=10 width=126) (actual time=60.655..64.761 rows=10.00 loops=1)"
"  Buffers: shared hit=3554"
"  ->  Sort  (cost=6343.37..6343.43 rows=25 width=126) (actual time=60.653..64.759 rows=10.00 loops=1)"
"        Sort Key: (count(c.c_custkey)) DESC"
"        Sort Method: top-N heapsort  Memory: 25kB"
"        Buffers: shared hit=3554"
"        ->  Finalize GroupAggregate  (cost=6335.29..6342.83 rows=25 width=126) (actual time=60.610..64.747 rows=25.00 loops=1)"
"              Group Key: n.n_name"
"              Buffers: shared hit=3554"
"              ->  Gather Merge  (cost=6335.29..6342.28 rows=60 width=126) (actual time=60.602..64.727 rows=50.00 loops=1)"
"                    Workers Planned: 2"
"                    Workers Launched: 2"
"                    Buffers: shared hit=3554"
"                    ->  Sort  (cost=5335.27..5335.33 rows=25 width=126) (actual time=22.266..22.268 rows=16.67 loops=3)"
"                          Sort Key: n.n_name"
"                          Sort Method: quicksort  Memory: 25kB"
"                          Buffers: shared hit=3554"
"                          Worker 0:  Sort Method: quicksort  Memory: 25kB"
"                          Worker 1:  Sort Method: quicksort  Memory: 25kB"
"                          ->  Partial HashAggregate  (cost=5334.44..5334.69 rows=25 width=126) (actual time=22.218..22.221 rows=16.67 loops=3)"
"                                Group Key: n.n_name"
"                                Batches: 1  Memory Usage: 32kB"
"                                Buffers: shared hit=3538"
"                                Worker 0:  Batches: 1  Memory Usage: 32kB"
"                                Worker 1:  Batches: 1  Memory Usage: 32kB"
"                                ->  Hash Join  (cost=1.56..5021.94 rows=62500 width=122) (actual time=0.141..14.182 rows=50000.00 loops=3)"
"                                      Hash Cond: (c.c_nationkey = n.n_nationkey)"
"                                      Buffers: shared hit=3538"
"                                      ->  Parallel Seq Scan on customer c  (cost=0.00..4161.00 rows=62500 width=8) (actual time=0.012..2.989 rows=50000.00 loops=3)"
"                                            Buffers: shared hit=3536"
"                                      ->  Hash  (cost=1.25..1.25 rows=25 width=122) (actual time=0.175..0.175 rows=25.00 loops=2)"
"                                            Buckets: 1024  Batches: 1  Memory Usage: 10kB"
"                                            Buffers: shared hit=2"
"                                            ->  Seq Scan on nation n  (cost=0.00..1.25 rows=25 width=122) (actual time=0.158..0.161 rows=25.00 loops=2)"
"                                                  Buffers: shared hit=2"
"Planning Time: 0.201 ms"
"Execution Time: 64.828 ms"
```

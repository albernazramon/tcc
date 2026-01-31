## Consulta 1

### Pergunta

Quero saber quantos clientes tenho em cada país e ordenar os resultados para mostrar primeiro os países com mais clientes.

```sql
EXPLAIN (ANALYZE, BUFFERS)

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

### Alucinações

Sem alucinações aparentes.

### Tempo total de execução da consulta (primeira execução) ~:

220 msec

### **Plano de execução**

```
"QUERY PLAN"
"Sort  (cost=6402.75..6403.22 rows=190 width=126) (actual time=62.552..67.618 rows=25.00 loops=1)"
"  Sort Key: (count(c.c_custkey)) DESC"
"  Sort Method: quicksort  Memory: 25kB"
"  Buffers: shared hit=3537"
"  ->  Finalize GroupAggregate  (cost=6338.27..6395.55 rows=190 width=126) (actual time=62.504..67.606 rows=25.00 loops=1)"
"        Group Key: n.n_name"
"        Buffers: shared hit=3537"
"        ->  Gather Merge  (cost=6338.27..6391.37 rows=456 width=126) (actual time=62.498..67.586 rows=75.00 loops=1)"
"              Workers Planned: 2"
"              Workers Launched: 2"
"              Buffers: shared hit=3537"
"              ->  Sort  (cost=5338.24..5338.72 rows=190 width=126) (actual time=25.249..25.251 rows=25.00 loops=3)"
"                    Sort Key: n.n_name"
"                    Sort Method: quicksort  Memory: 25kB"
"                    Buffers: shared hit=3537"
"                    Worker 0:  Sort Method: quicksort  Memory: 25kB"
"                    Worker 1:  Sort Method: quicksort  Memory: 25kB"
"                    ->  Partial HashAggregate  (cost=5329.15..5331.05 rows=190 width=126) (actual time=25.187..25.192 rows=25.00 loops=3)"
"                          Group Key: n.n_name"
"                          Batches: 1  Memory Usage: 32kB"
"                          Buffers: shared hit=3521"
"                          Worker 0:  Batches: 1  Memory Usage: 32kB"
"                          Worker 1:  Batches: 1  Memory Usage: 32kB"
"                          ->  Hash Join  (cost=14.28..5016.65 rows=62500 width=122) (actual time=0.265..16.266 rows=50000.00 loops=3)"
"                                Hash Cond: (c.c_nationkey = n.n_nationkey)"
"                                Buffers: shared hit=3521"
"                                ->  Parallel Seq Scan on customer c  (cost=0.00..4143.00 rows=62500 width=8) (actual time=0.010..3.332 rows=50000.00 loops=3)"
"                                      Buffers: shared hit=3518"
"                                ->  Hash  (cost=11.90..11.90 rows=190 width=122) (actual time=0.245..0.245 rows=25.00 loops=3)"
"                                      Buckets: 1024  Batches: 1  Memory Usage: 10kB"
"                                      Buffers: shared hit=3"
"                                      ->  Seq Scan on nation n  (cost=0.00..11.90 rows=190 width=122) (actual time=0.234..0.236 rows=25.00 loops=3)"
"                                            Buffers: shared hit=3"
"Planning Time: 0.117 ms"
"Execution Time: 67.703 ms"
```

---

## Consulta 2

### Pergunta

Quais são os 5 clientes com maior valor total de pedidos?

```sql
SELECT c.c_name
FROM customer c
JOIN orders o ON c.c_custkey = o.o_custkey
GROUP BY c.c_custkey
ORDER BY SUM(o.o_totalprice) DESC
LIMIT 5;
```

### Alucinações

A consulta gerada não utiliza c.c_name no GROUP BY, o que é um erro SQL.

#### CORREÇÃO: usar c.c_name no GROUP BY.

### Tempo total de execução da consulta (primeira execução) ~:

662 msec

### **Plano de execução**

```
"QUERY PLAN"
"Limit  (cost=169840.63..169840.65 rows=5 width=27) (actual time=690.206..695.841 rows=5.00 loops=1)"
"  Buffers: shared hit=3830 read=25918, temp read=1387 written=1390"
"  ->  Sort  (cost=169840.63..170215.63 rows=150000 width=27) (actual time=690.205..695.839 rows=5.00 loops=1)"
"        Sort Key: (sum(o.o_totalprice)) DESC"
"        Sort Method: top-N heapsort  Memory: 25kB"
"        Buffers: shared hit=3830 read=25918, temp read=1387 written=1390"
"        ->  Finalize GroupAggregate  (cost=121221.26..167349.19 rows=150000 width=27) (actual time=589.260..684.830 rows=100000.00 loops=1)"
"              Group Key: c.c_custkey, c.c_name"
"              Buffers: shared hit=3830 read=25918, temp read=1387 written=1390"
"              ->  Gather Merge  (cost=121221.26..163149.19 rows=360000 width=27) (actual time=589.248..640.314 rows=297940.00 loops=1)"
"                    Workers Planned: 2"
"                    Workers Launched: 2"
"                    Buffers: shared hit=3830 read=25918, temp read=1387 written=1390"
"                    ->  Sort  (cost=120221.23..120596.23 rows=150000 width=27) (actual time=547.773..557.610 rows=99313.33 loops=3)"
"                          Sort Key: c.c_custkey, c.c_name"
"                          Sort Method: external merge  Disk: 3696kB"
"                          Buffers: shared hit=3830 read=25918, temp read=1387 written=1390"
"                          Worker 0:  Sort Method: external merge  Disk: 3704kB"
"                          Worker 1:  Sort Method: external merge  Disk: 3696kB"
"                          ->  Partial HashAggregate  (cost=93689.36..103734.28 rows=150000 width=27) (actual time=492.818..513.027 rows=99313.33 loops=3)"
"                                Group Key: c.c_custkey, c.c_name"
"                                Planned Partitions: 4  Batches: 1  Memory Usage: 7705kB"
"                                Buffers: shared hit=3800 read=25918"
"                                Worker 0:  Batches: 1  Memory Usage: 7705kB"
"                                Worker 1:  Batches: 1  Memory Usage: 7705kB"
"                                ->  Parallel Hash Join  (cost=4924.25..42322.17 rows=625000 width=27) (actual time=15.734..291.029 rows=500000.00 loops=3)"
"                                      Hash Cond: (o.o_custkey = c.c_custkey)"
"                                      Buffers: shared hit=3800 read=25918"
"                                      ->  Parallel Seq Scan on orders o  (cost=0.00..32450.00 rows=625000 width=8) (actual time=0.250..35.562 rows=500000.00 loops=3)"
"                                            Buffers: shared hit=282 read=25918"
"                                      ->  Parallel Hash  (cost=4143.00..4143.00 rows=62500 width=23) (actual time=15.167..15.168 rows=50000.00 loops=3)"
"                                            Buckets: 262144  Batches: 1  Memory Usage: 10272kB"
"                                            Buffers: shared hit=3518"
"                                            ->  Parallel Seq Scan on customer c  (cost=0.00..4143.00 rows=62500 width=23) (actual time=0.008..17.978 rows=150000.00 loops=1)"
"                                                  Buffers: shared hit=3518"
"Planning Time: 0.154 ms"
"Execution Time: 697.486 ms"
```

---

## Consulta 3

### Pergunta

Quais são as instruções de envio mais repetidas?

```sql
SELECT l_shipmode
FROM lineitem
GROUP BY l_shipmode
ORDER BY count(*) DESC
LIMIT 1;
```

### Alucinações

Sem alucinações aparentes.

### Tempo total de execução da consulta (primeira execução) ~:

903 msec

### **Plano de execução**

```
"QUERY PLAN"
"Limit  (cost=112819.28..112819.29 rows=1 width=13) (actual time=517.107..520.946 rows=1.00 loops=1)"
"  Buffers: shared hit=298 read=83884"
"  ->  Sort  (cost=112819.28..112819.30 rows=7 width=13) (actual time=517.106..520.944 rows=1.00 loops=1)"
"        Sort Key: (count(*)) DESC"
"        Sort Method: top-N heapsort  Memory: 25kB"
"        Buffers: shared hit=298 read=83884"
"        ->  Finalize GroupAggregate  (cost=112817.11..112819.25 rows=7 width=13) (actual time=517.089..520.937 rows=7.00 loops=1)"
"              Group Key: l_shipmode"
"              Buffers: shared hit=298 read=83884"
"              ->  Gather Merge  (cost=112817.11..112819.09 rows=17 width=13) (actual time=517.083..520.927 rows=21.00 loops=1)"
"                    Workers Planned: 2"
"                    Workers Launched: 2"
"                    Buffers: shared hit=298 read=83884"
"                    ->  Sort  (cost=111817.09..111817.11 rows=7 width=13) (actual time=444.608..444.609 rows=7.00 loops=3)"
"                          Sort Key: l_shipmode"
"                          Sort Method: quicksort  Memory: 25kB"
"                          Buffers: shared hit=298 read=83884"
"                          Worker 0:  Sort Method: quicksort  Memory: 25kB"
"                          Worker 1:  Sort Method: quicksort  Memory: 25kB"
"                          ->  Partial HashAggregate  (cost=111816.92..111816.99 rows=7 width=13) (actual time=444.577..444.578 rows=7.00 loops=3)"
"                                Group Key: l_shipmode"
"                                Batches: 1  Memory Usage: 32kB"
"                                Buffers: shared hit=282 read=83884"
"                                Worker 0:  Batches: 1  Memory Usage: 32kB"
"                                Worker 1:  Batches: 1  Memory Usage: 32kB"
"                                ->  Parallel Seq Scan on lineitem  (cost=0.00..102599.95 rows=1843395 width=5) (actual time=0.376..94.940 rows=1474553.00 loops=3)"
"                                      Buffers: shared hit=282 read=83884"
"Planning Time: 0.080 ms"
"Execution Time: 520.994 ms"
```

---

## Consulta 4

### Pergunta

Quero saber quantos clientes tenho em cada país e ordenar os resultados para mostrar primeiro os países com mais clientes.

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

### Alucinações

A consulta gerada limita os resultados, mas a pergunta não exige isso.

### Tempo total de execução da consulta (primeira execução) ~:

95 msec

### **Plano de execução**

```
"QUERY PLAN"
"Limit  (cost=6399.66..6399.68 rows=10 width=126) (actual time=59.904..63.726 rows=10.00 loops=1)"
"  Buffers: shared hit=3536"
"  ->  Sort  (cost=6399.66..6400.13 rows=190 width=126) (actual time=59.904..63.724 rows=10.00 loops=1)"
"        Sort Key: (count(c.c_custkey)) DESC"
"        Sort Method: top-N heapsort  Memory: 25kB"
"        Buffers: shared hit=3536"
"        ->  Finalize GroupAggregate  (cost=6338.27..6395.55 rows=190 width=126) (actual time=59.876..63.714 rows=25.00 loops=1)"
"              Group Key: n.n_name"
"              Buffers: shared hit=3536"
"              ->  Gather Merge  (cost=6338.27..6391.37 rows=456 width=126) (actual time=59.868..63.700 rows=50.00 loops=1)"
"                    Workers Planned: 2"
"                    Workers Launched: 2"
"                    Buffers: shared hit=3536"
"                    ->  Sort  (cost=5338.24..5338.72 rows=190 width=126) (actual time=23.616..23.617 rows=16.67 loops=3)"
"                          Sort Key: n.n_name"
"                          Sort Method: quicksort  Memory: 25kB"
"                          Buffers: shared hit=3536"
"                          Worker 0:  Sort Method: quicksort  Memory: 25kB"
"                          Worker 1:  Sort Method: quicksort  Memory: 25kB"
"                          ->  Partial HashAggregate  (cost=5329.15..5331.05 rows=190 width=126) (actual time=23.567..23.569 rows=16.67 loops=3)"
"                                Group Key: n.n_name"
"                                Batches: 1  Memory Usage: 32kB"
"                                Buffers: shared hit=3520"
"                                Worker 0:  Batches: 1  Memory Usage: 32kB"
"                                Worker 1:  Batches: 1  Memory Usage: 32kB"
"                                ->  Hash Join  (cost=14.28..5016.65 rows=62500 width=122) (actual time=0.145..15.078 rows=50000.00 loops=3)"
"                                      Hash Cond: (c.c_nationkey = n.n_nationkey)"
"                                      Buffers: shared hit=3520"
"                                      ->  Parallel Seq Scan on customer c  (cost=0.00..4143.00 rows=62500 width=8) (actual time=0.005..3.103 rows=50000.00 loops=3)"
"                                            Buffers: shared hit=3518"
"                                      ->  Hash  (cost=11.90..11.90 rows=190 width=122) (actual time=0.201..0.201 rows=25.00 loops=2)"
"                                            Buckets: 1024  Batches: 1  Memory Usage: 10kB"
"                                            Buffers: shared hit=2"
"                                            ->  Seq Scan on nation n  (cost=0.00..11.90 rows=190 width=122) (actual time=0.188..0.191 rows=25.00 loops=2)"
"                                                  Buffers: shared hit=2"
"Planning Time: 0.130 ms"
"Execution Time: 63.812 ms"
```

---

## Consulta 5

### Pergunta

Calcular a quantidade total de peças vendidas em cada região, excluindo regiões onde o número de tipos distintos de peças é inferior a 3.

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

### Alucinações

Sem alucinações aparentes.

### Tempo total de execução da consulta (primeira execução) ~:

276 msec

### **Plano de execução**

```
"QUERY PLAN"
"GroupAggregate  (cost=110657.62..111189.08 rows=63 width=126) (actual time=289.166..293.888 rows=5.00 loops=1)"
"  Group Key: r.r_name"
"  Filter: (count(DISTINCT li.l_partkey) >= 3)"
"  Buffers: shared hit=882 read=83320"
"  ->  Gather Merge  (cost=110657.62..111154.70 rows=4268 width=126) (actual time=289.124..293.816 rows=506.00 loops=1)"
"        Workers Planned: 2"
"        Workers Launched: 2"
"        Buffers: shared hit=882 read=83320"
"        ->  Sort  (cost=109657.60..109662.04 rows=1778 width=126) (actual time=251.096..251.105 rows=168.67 loops=3)"
"              Sort Key: r.r_name, li.l_partkey"
"              Sort Method: quicksort  Memory: 31kB"
"              Buffers: shared hit=882 read=83320"
"              Worker 0:  Sort Method: quicksort  Memory: 29kB"
"              Worker 1:  Sort Method: quicksort  Memory: 30kB"
"              ->  Hash Join  (cost=31.16..109561.62 rows=1778 width=126) (actual time=3.319..250.877 rows=168.67 loops=3)"
"                    Hash Cond: (li.l_partkey = n.n_nationkey)"
"                    Buffers: shared hit=852 read=83320"
"                    ->  Parallel Seq Scan on lineitem li  (cost=0.00..102599.95 rows=1843395 width=8) (actual time=0.288..98.192 rows=1474553.00 loops=3)"
"                          Buffers: shared hit=846 read=83320"
"                    ->  Hash  (cost=28.79..28.79 rows=190 width=122) (actual time=0.402..0.404 rows=25.00 loops=3)"
"                          Buckets: 1024  Batches: 1  Memory Usage: 10kB"
"                          Buffers: shared hit=6"
"                          ->  Hash Join  (cost=14.28..28.79 rows=190 width=122) (actual time=0.389..0.395 rows=25.00 loops=3)"
"                                Hash Cond: (r.r_regionkey = n.n_regionkey)"
"                                Buffers: shared hit=6"
"                                ->  Seq Scan on region r  (cost=0.00..11.90 rows=190 width=122) (actual time=0.172..0.172 rows=5.00 loops=3)"
"                                      Buffers: shared hit=3"
"                                ->  Hash  (cost=11.90..11.90 rows=190 width=8) (actual time=0.206..0.207 rows=25.00 loops=3)"
"                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB"
"                                      Buffers: shared hit=3"
"                                      ->  Seq Scan on nation n  (cost=0.00..11.90 rows=190 width=8) (actual time=0.192..0.195 rows=25.00 loops=3)"
"                                            Buffers: shared hit=3"
"Planning Time: 0.147 ms"
"Execution Time: 293.969 ms"
```

---

## Consulta 6

### Pergunta

Encontrar a porcentagem média de desconto para itens do pedido associados a clientes da região 'West' que têm saldo de crédito maior que $50000, ordenado pela data de envio em ordem decrescente.

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

### Alucinações

1. O SELECT não seleciona nada. Ajustei para SELECT \*.
2. Foi necessário alterar a região para uma existente e reduzir c_acctbal para 1000 (isso não é erro do LLM, pois ele conhece apenas o esquema, não os valores).

### Tempo total de execução da consulta (primeira execução) ~:

- Após as alterações na consulta:
  1 secs 195 msec

### **Plano de execução**

```
"QUERY PLAN"
"Gather Merge  (cost=150417.43..152627.85 rows=18979 width=11) (actual time=1089.644..1208.717 rows=727692.00 loops=1)"
"  Workers Planned: 2"
"  Workers Launched: 2"
"  Buffers: shared hit=6356 read=107546, temp read=1338 written=1341"
"  ->  Sort  (cost=149417.41..149437.18 rows=7908 width=11) (actual time=1023.207..1047.841 rows=242564.00 loops=3)"
"        Sort Key: l.l_shipdate DESC"
"        Sort Method: external merge  Disk: 3760kB"
"        Buffers: shared hit=6356 read=107546, temp read=1338 written=1341"
"        Worker 0:  Sort Method: external merge  Disk: 3184kB"
"        Worker 1:  Sort Method: external merge  Disk: 3760kB"
"        ->  Parallel Hash Join  (cost=39359.77..148905.40 rows=7908 width=11) (actual time=148.456..468.598 rows=242564.00 loops=3)"
"              Hash Cond: (l.l_orderkey = o.o_orderkey)"
"              Buffers: shared hit=6340 read=107546"
"              ->  Parallel Seq Scan on lineitem l  (cost=0.00..102599.95 rows=1843395 width=15) (actual time=0.480..97.399 rows=1474553.00 loops=3)"
"                    Buffers: shared hit=1692 read=82474"
"              ->  Parallel Hash  (cost=39326.26..39326.26 rows=2681 width=4) (actual time=147.928..147.983 rows=82206.67 loops=3)"
"                    Buckets: 262144 (originalmente 8192)  Batches: 1 (originalmente 1)  Memory Usage: 13760kB"
"                    Buffers: shared hit=4648 read=25072"
"                    ->  Parallel Hash Join  (cost=4521.34..39326.26 rows=2681 width=4) (actual time=11.582..125.224 rows=82206.67 loops=3)"
"                          Hash Cond: (o.o_custkey = c.c_custkey)"
"                          Buffers: shared hit=4648 read=25072"
"                          ->  Parallel Seq Scan on orders o  (cost=0.00..32450.00 rows=625000 width=8) (actual time=0.289..38.851 rows=500000.00 loops=3)"
"                                Buffers: shared hit=1128 read=25072"
"                          ->  Parallel Hash  (cost=4517.99..4517.99 rows=268 width=4) (actual time=11.275..11.277 rows=8222.00 loops=3)"
"                                Buckets: 32768 (originalmente 1024)  Batches: 1 (originalmente 1)  Memory Usage: 1496kB"
"                                Buffers: shared hit=3520"
"                                ->  Hash Join  (cost=25.02..4517.99 rows=268 width=4) (actual time=0.052..29.857 rows=24666.00 loops=1)"
"                                      Hash Cond: (c.c_nationkey = n.n_nationkey)"
"                                      Buffers: shared hit=3520"
"                                      ->  Parallel Seq Scan on customer c  (cost=0.00..4299.25 rows=50944 width=8) (actual time=0.008..20.358 rows=122435.00 loops=1)"
"                                            Filter: (c_acctbal > '1000'::double precision)"
"                                            Rows Removed by Filter: 27565"
"                                            Buffers: shared hit=3518"
"                                      ->  Hash  (cost=25.01..25.01 rows=1 width=4) (actual time=0.037..0.040 rows=5.00 loops=1)"
"                                            Buckets: 1024  Batches: 1  Memory Usage: 9kB"
"                                            Buffers: shared hit=2"
"                                            ->  Hash Join  (cost=12.39..25.01 rows=1 width=4) (actual time=0.032..0.037 rows=5.00 loops=1)"
"                                                  Hash Cond: (n.n_regionkey = r.r_regionkey)"
"                                                  Buffers: shared hit=2"
"                                                  ->  Seq Scan on nation n  (cost=0.00..11.90 rows=190 width=8) (actual time=0.010..0.012 rows=25.00 loops=1)"
"                                                        Buffers: shared hit=1"
"                                                  ->  Hash  (cost=12.38..12.38 rows=1 width=4) (actual time=0.011..0.012 rows=1.00 loops=1)"
"                                                        Buckets: 1024  Batches: 1  Memory Usage: 9kB"
"                                                        Buffers: shared hit=1"
"                                                        ->  Seq Scan on region r  (cost=0.00..12.38 rows=1 width=4) (actual time=0.007..0.008 rows=1.00 loops=1)"
"                                                              Filter: ((r_name)::text = 'ASIA'::text)"
"                                                              Rows Removed by Filter: 4"
"                                                              Buffers: shared hit=1"
"Planning Time: 0.237 ms"
"Execution Time: 1234.115 ms"
```

---

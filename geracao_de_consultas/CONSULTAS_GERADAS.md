## Consultas

Essas consultas foram geradas pelo Gemma 3.

### Consulta 1 - Quero saber quantos clientes tenho em cada país e ordenar os resultados para mostrar primeiro os países com mais clientes.

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

### Consulta 2 - Quais são os 5 clientes com maior valor total de pedidos?

```sql
SELECT c.c_name
FROM customer c
JOIN orders o ON c.c_custkey = o.o_custkey
GROUP BY c.c_custkey
ORDER BY SUM(o.o_totalprice) DESC
LIMIT 5;
```

### Consulta 3 - Quais são as instruções de envio mais repetidas?

```sql
SELECT l_shipmode
FROM lineitem
GROUP BY l_shipmode
ORDER BY count(*) DESC
LIMIT 1;
```

### Consulta 4 - Quero saber quantos clientes tenho em cada país e ordenar os resultados para mostrar primeiro os países com mais clientes.

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

### Consulta 5 - Calcular a quantidade total de peças vendidas em cada região, excluindo regiões onde o número de tipos distintos de peças é inferior a 3.

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

### Consulta 6 - Encontrar a porcentagem média de desconto para itens do pedido associados a clientes da região 'West' que têm saldo de crédito maior que $50000, ordenado pela data de envio em ordem decrescente.

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

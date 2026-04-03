# Comparação de Resultados: Cenário 5

## Queries Analisadas

### Pré-Otimização:

**Problema:** A consulta sofre com varreduras sequenciais (Seq Scans) em tabelas grandes devido à falta de índices em colunas altamente seletivas como `region.r_name` e `orders.o_orderdate`. Além disso, a ausência de índices em chaves estrangeiras (`o_custkey`, `l_orderkey`, `l_suppkey`) prejudica a eficiência das múltiplas junções, forçando o uso de Hash Joins caros e ordenações explícitas para o `GROUP BY` e `ORDER BY`.

```sql
-- using default substitutions


select
	n_name,
	sum(l_extendedprice * (1 - l_discount)) as revenue
from
	customer,
	orders,
	lineitem,
	supplier,
	nation,
	region
where
	c_custkey = o_custkey
	and l_orderkey = o_orderkey
	and l_suppkey = s_suppkey
	and c_nationkey = s_nationkey
	and s_nationkey = n_nationkey
	and n_regionkey = r_regionkey
	and r_name = 'ASIA'
	and o_orderdate >= date '1994-01-01'
	and o_orderdate < date '1994-01-01' + interval '1 year'
group by
	n_name
order by
	revenue desc;
```

### Pós-Otimização:

**Alterações:** A consulta foi reescrita utilizando **JOIN explícito** para melhor legibilidade. A otimização foca na criação de uma série de índices estratégicos: índices B-tree em `r_name` e `o_orderdate` para acelerar os filtros, e índices em todas as chaves estrangeiras envolvidas nas junções. Isso permite que o otimizador utilize **Nested Loop Joins com Index Scan**, reduzindo drasticamente o volume de dados processados e agilizando as etapas de agregação e ordenação final.

```sql
-- Filtros
CREATE INDEX idx_region_r_name ON public.region (r_name);
CREATE INDEX idx_orders_o_orderdate ON public.orders (o_orderdate);

-- Junções (Nation, Supplier, Customer)
CREATE INDEX idx_nation_n_regionkey ON public.nation (n_regionkey);
CREATE INDEX idx_supplier_s_nationkey ON public.supplier (s_nationkey);
CREATE INDEX idx_customer_c_nationkey ON public.customer (c_nationkey);

-- Junções (Orders, Lineitem)
CREATE INDEX idx_orders_o_custkey ON public.orders (o_custkey);
CREATE INDEX idx_lineitem_l_orderkey ON public.lineitem (l_orderkey);
CREATE INDEX idx_lineitem_l_suppkey ON public.lineitem (l_suppkey);

SELECT
    n.n_name,
    SUM(l.l_extendedprice * (1 - l.l_discount)) AS revenue
FROM
    region AS r
JOIN
    nation AS n ON n.n_regionkey = r.r_regionkey
JOIN
    supplier AS s ON s.s_nationkey = n.n_nationkey
JOIN
    customer AS c ON c.c_nationkey = s.s_nationkey
JOIN
    orders AS o ON o.o_custkey = c.c_custkey
JOIN
    lineitem AS l ON l.l_orderkey = o.o_orderkey AND l.l_suppkey = s.s_suppkey
WHERE
    r.r_name = 'ASIA'
    AND o.o_orderdate >= DATE '1994-01-01'
    AND o.o_orderdate < DATE '1994-01-01' + INTERVAL '1 year'
GROUP BY
    n.n_name
ORDER BY
    revenue DESC;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 85.487,27 ms   |                |                     |
| **Custo Inicial Estimado** | 4.141.853,84   |                |                     |
| **Custo Total Estimado**   | 4.141.853,90   |                |                     |
| **Linhas**                 | 25             |                |                     |
| **Memória: Hit**           | 21             |                |                     |
| **Memória: Read**          | 2.849.349      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 279.294        |                |                     |
| **Temp Written**           | 279.892        |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

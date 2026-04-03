# Comparação de Resultados: Cenário 7

## Queries Analisadas

### Pré-Otimização:

**Problema:** A consulta original sofre com a ausência de índices, forçando varreduras sequenciais (`Seq Scan`) em tabelas grandes como `lineitem`. Joins entre múltiplas tabelas sem índices em chaves estrangeiras resultam em `Hash Joins` caros, e filtros como `l_shipdate BETWEEN` e condições de nação exigem processamento pesado de I/O. Além disso, a ordenação e agregação final impõem um custo alto de CPU e memória.

```sql
-- using default substitutions


select
	supp_nation,
	cust_nation,
	l_year,
	sum(volume) as revenue
from
	(
		select
			n1.n_name as supp_nation,
			n2.n_name as cust_nation,
			extract(year from l_shipdate) as l_year,
			l_extendedprice * (1 - l_discount) as volume
		from
			supplier,
			lineitem,
			orders,
			customer,
			nation n1,
			nation n2
		where
			s_suppkey = l_suppkey
			and o_orderkey = l_orderkey
			and c_custkey = o_custkey
			and s_nationkey = n1.n_nationkey
			and c_nationkey = n2.n_nationkey
			and (
				(n1.n_name = 'FRANCE' and n2.n_name = 'GERMANY')
				or (n1.n_name = 'GERMANY' and n2.n_name = 'FRANCE')
			)
			and l_shipdate between date '1995-01-01' and date '1996-12-31'
	) as shipping
group by
	supp_nation,
	cust_nation,
	l_year
order by
	supp_nation,
	cust_nation,
	l_year;
```

### Pós-Otimização:

**Alterações:** A consulta foi simplificada através do "achatamento" da subquery, integrando as operações diretamente com `JOIN`s explícitos. Foram recomendados índices estratégicos: PKs em todas as tabelas, índices em chaves estrangeiras (`l_suppkey`, `o_custkey`, etc.) para otimizar os joins, e índices em colunas de filtro (`l_shipdate`, `n_name`). Isso permite que o PostgreSQL utilize `Index Scans` e `Bitmap Index Scans`, reduzindo drasticamente o volume de dados lidos e agilizando a agregação e ordenação.

```sql
-- Índices em Chaves Estrangeiras
CREATE INDEX idx_lineitem_suppkey ON public.lineitem (l_suppkey);
CREATE INDEX idx_orders_custkey ON public.orders (o_custkey);
CREATE INDEX idx_supplier_nationkey ON public.supplier (s_nationkey);
CREATE INDEX idx_customer_nationkey ON public.customer (c_nationkey);

-- Índices para Filtros e Ordenação
CREATE INDEX idx_lineitem_shipdate ON public.lineitem (l_shipdate);
CREATE INDEX idx_nation_name ON public.nation (n_name);

SELECT
    n1.n_name AS supp_nation,
    n2.n_name AS cust_nation,
    EXTRACT(YEAR FROM l.l_shipdate) AS l_year,
    SUM(l.l_extendedprice * (1 - l.l_discount)) AS revenue
FROM
    lineitem l
JOIN
    supplier s ON s.s_suppkey = l.l_suppkey
JOIN
    orders o ON o.o_orderkey = l.l_orderkey
JOIN
    customer c ON c.c_custkey = o.o_custkey
JOIN
    nation n1 ON s.s_nationkey = n1.n_nationkey
JOIN
    nation n2 ON c.c_nationkey = n2.n_nationkey
WHERE
    l.l_shipdate BETWEEN DATE '1995-01-01' AND DATE '1996-12-31'
    AND (
        (n1.n_name = 'FRANCE' AND n2.n_name = 'GERMANY')
        OR (n1.n_name = 'GERMANY' AND n2.n_name = 'FRANCE')
    )
GROUP BY
    n1.n_name,
    n2.n_name,
    l_year
ORDER BY
    n1.n_name,
    n2.n_name,
    l_year;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 83.994,40 ms   |                |                     |
| **Custo Inicial Estimado** | 3.916.911,81   |                |                     |
| **Custo Total Estimado**   | 3.921.163,20   |                |                     |
| **Linhas**                 | 10.068         |                |                     |
| **Memória: Hit**           | 33             |                |                     |
| **Memória: Read**          | 2.849.348      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 40.093         |                |                     |
| **Temp Written**           | 40.412         |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

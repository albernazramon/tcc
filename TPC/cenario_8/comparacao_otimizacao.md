# Comparação de Resultados: Cenário 8

## Queries Analisadas

### Pré-Otimização:

**Problema:** A consulta original apresenta lentidão devido a varreduras sequenciais (`Seq Scans`) em tabelas grandes como `orders`, `part` e `lineitem`, causadas pela falta de índices em colunas de filtro (`o_orderdate`, `p_type`, `r_name`). Joins ineficientes e a estrutura de subconsulta também contribuem para o alto custo de CPU e I/O, além da necessidade de ordenação explícita para o agrupamento por ano.

```sql
-- using default substitutions


select
	o_year,
	sum(case
		when nation = 'BRAZIL' then volume
		else 0
	end) / sum(volume) as mkt_share
from
	(
		select
			extract(year from o_orderdate) as o_year,
			l_extendedprice * (1 - l_discount) as volume,
			n2.n_name as nation
		from
			part,
			supplier,
			lineitem,
			orders,
			customer,
			nation n1,
			nation n2,
			region
		where
			p_partkey = l_partkey
			and s_suppkey = l_suppkey
			and l_orderkey = o_orderkey
			and o_custkey = c_custkey
			and c_nationkey = n1.n_nationkey
			and n1.n_regionkey = r_regionkey
			and r_name = 'AMERICA'
			and s_nationkey = n2.n_nationkey
			and o_orderdate between date '1995-01-01' and date '1996-12-31'
			and p_type = 'ECONOMY ANODIZED STEEL'
	) as all_nations
group by
	o_year
order by
	o_year;
```

### Pós-Otimização:

**Alterações:** A subconsulta foi eliminada ("achatamento") e substituída por `JOIN`s explícitos para simplificar o plano de execução. Foram recomendados índices estratégicos para as colunas de filtro (`o_orderdate`, `p_type`, `r_name`) e para todas as chaves estrangeiras envolvidas nas junções. Essas alterações permitem que o PostgreSQL utilize `Index Scans` ou `Bitmap Index Scans`, resultando em um processamento muito mais rápido e eficiente de filtros e junções.

```sql
-- Índices para colunas de filtro
CREATE INDEX IF NOT EXISTS idx_orders_o_orderdate ON public.orders (o_orderdate);
CREATE INDEX IF NOT EXISTS idx_part_p_type ON public.part (p_type);
CREATE INDEX IF NOT EXISTS idx_region_r_name ON public.region (r_name);

-- Índices para chaves estrangeiras (FKs)
CREATE INDEX IF NOT EXISTS idx_lineitem_l_partkey ON public.lineitem (l_partkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_l_suppkey ON public.lineitem (l_suppkey);
CREATE INDEX IF NOT EXISTS idx_orders_o_custkey ON public.orders (o_custkey);
CREATE INDEX IF NOT EXISTS idx_customer_c_nationkey ON public.customer (c_nationkey);
CREATE INDEX IF NOT EXISTS idx_nation_n_regionkey ON public.nation (n_regionkey);
CREATE INDEX IF NOT EXISTS idx_supplier_s_nationkey ON public.supplier (s_nationkey);

SELECT
    EXTRACT(YEAR FROM o.o_orderdate) AS o_year,
    SUM(CASE
        WHEN n2.n_name = 'BRAZIL' THEN l.l_extendedprice * (1 - l.l_discount)
        ELSE 0
    END) / SUM(l.l_extendedprice * (1 - l.l_discount)) AS mkt_share
FROM
    part p
JOIN
    lineitem l ON p.p_partkey = l.l_partkey
JOIN
    supplier s ON s.s_suppkey = l.l_suppkey
JOIN
    orders o ON l.l_orderkey = o.o_orderkey
JOIN
    customer c ON o.o_custkey = c.c_custkey
JOIN
    nation n1 ON c.c_nationkey = n1.n_nationkey
JOIN
    region r ON n1.n_regionkey = r.r_regionkey
JOIN
    nation n2 ON s.s_nationkey = n2.n_nationkey
WHERE
    r.r_name = 'AMERICA'
    AND o.o_orderdate BETWEEN DATE '1995-01-01' AND DATE '1996-12-31'
    AND p.p_type = 'ECONOMY ANODIZED STEEL'
GROUP BY
    o_year
ORDER BY
    o_year;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 84.691,15 ms   |                |                     |
| **Custo Inicial Estimado** | 3.911.934,81   |                |                     |
| **Custo Total Estimado**   | 3.913.207,49   |                |                     |
| **Linhas**                 | 2.406          |                |                     |
| **Memória: Hit**           | 21             |                |                     |
| **Memória: Read**          | 2.931.267      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 39.367         |                |                     |
| **Temp Written**           | 39.436         |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

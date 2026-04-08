# Comparação de Resultados: Cenário 15

## Queries Analisadas

### Pré-Otimização:

**Problema:** A criação e descarte de uma view temporária introduz sobrecarga desnecessária. Além disso, a view é referenciada duas vezes, o que pode levar à reexecução redundante da agregação e do filtro na tabela `lineitem`. A falta de índices em `l_shipdate` e `l_suppkey` força varreduras sequenciais (`Seq Scan`) custosas em tabelas grandes.

```sql
-- using default substitutions

create view revenue0 (supplier_no, total_revenue) as
	select
		l_suppkey,
		sum(l_extendedprice * (1 - l_discount))
	from
		lineitem
	where
		l_shipdate >= date '1996-01-01'
		and l_shipdate < date '1996-01-01' + interval '3 months'
	group by
		l_suppkey;


select
	s_suppkey,
	s_name,
	s_address,
	s_phone,
	total_revenue
from
	supplier,
	revenue0
where
	s_suppkey = supplier_no
	and total_revenue = (
		select
			max(total_revenue)
		from
			revenue0
	)
order by
	s_suppkey;

drop view revenue0;
```

### Pós-Otimização:

**Alterações:** A view temporária foi substituída por uma **CTE (Common Table Expression)**, permitindo que o otimizador visualize melhor a consulta e evite recomputações redundantes. Foram recomendados índices estratégicos: um índice composto em `lineitem` (`l_shipdate`, `l_suppkey`) para acelerar simultaneamente o filtro de data e o agrupamento, e um índice em `supplier.s_suppkey` para otimizar a junção final.

```sql
-- Índice composto para lineitem
CREATE INDEX idx_lineitem_shipdate_suppkey ON public.lineitem (l_shipdate, l_suppkey);

-- Índice para supplier
CREATE INDEX idx_supplier_suppkey ON public.supplier (s_suppkey);

WITH supplier_revenue AS (
    SELECT
        l_suppkey,
        sum(l_extendedprice * (1 - l_discount)) AS total_revenue
    FROM
        lineitem
    WHERE
        l_shipdate >= date '1996-01-01'
        AND l_shipdate < date '1996-04-01'
    GROUP BY
        l_suppkey
)
SELECT
    s.s_suppkey,
    s.s_name,
    s.s_address,
    s.s_phone,
    sr.total_revenue
FROM
    supplier s
JOIN
    supplier_revenue sr ON s.s_suppkey = sr.l_suppkey
WHERE
    sr.total_revenue = (SELECT max(total_revenue) FROM supplier_revenue)
ORDER BY
    s.s_suppkey;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 37.164,97 ms   | 16.554,10 ms   |                     |
| **Custo Inicial Estimado** | 3.221.848,20   | 1.619.241,09   |                     |
| **Custo Total Estimado**   | 3.253.431,90   | 1.624.426,91   |                     |
| **Linhas**                 | 497            | 492            |                     |
| **Memória: Hit**           | 310            | 14             |                     |
| **Memória: Read**          | 2.252.193      | 1.125.131      |                     |
| **Memória: Dirtied**       | -              | -              |                     |
| **Memória: Written**       | 42.107         | 20.840         |                     |
| **Temp Read**              | 26.121         | 12.909         |                     |
| **Temp Written**           | -              | -              |                     |

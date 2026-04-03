# Comparação de Resultados: Cenário 21

## Queries Analisadas

### Pré-Otimização:

**Problema:** A consulta original sofre com o uso de duas subqueries correlacionadas (`EXISTS` e `NOT EXISTS`) no `WHERE`, que são reavaliadas para cada linha da tabela `lineitem`, gerando um desempenho extremamente lento. Além disso, a falta de índices adequados em colunas de filtro (`o_orderstatus`, `n_name`) e em chaves estrangeiras obriga o planejador a recorrer a varreduras sequenciais e `Bitmap Scans` caros.

```sql
-- using default substitutions


select
	s_name,
	count(*) as numwait
from
	supplier,
	lineitem l1,
	orders,
	nation
where
	s_suppkey = l1.l_suppkey
	and o_orderkey = l1.l_orderkey
	and o_orderstatus = 'F'
	and l1.l_receiptdate > l1.l_commitdate
	and exists (
		select
			*
		from
			lineitem l2
		where
			l2.l_orderkey = l1.l_orderkey
			and l2.l_suppkey <> l1.l_suppkey
	)
	and not exists (
		select
			*
		from
			lineitem l3
		where
			l3.l_orderkey = l1.l_orderkey
			and l3.l_suppkey <> l1.l_suppkey
			and l3.l_receiptdate > l3.l_commitdate
	)
	and s_nationkey = n_nationkey
	and n_name = 'SAUDI ARABIA'
group by
	s_name
order by
	numwait desc,
	s_name
limit 100;
```

### Pós-Otimização:

**Alterações:** As subqueries correlacionadas foram substituídas por **CTEs (Common Table Expressions)** e **Anti-Joins (`LEFT JOIN / IS NULL`)**, permitindo que o PostgreSQL as processe de forma muito mais eficiente. Foram recomendados índices estratégicos para acelerar os filtros e as múltiplas junções, com destaque para um **índice composto abrangente em `lineitem`** (`l_orderkey`, `l_suppkey`, `l_receiptdate`, `l_commitdate`), que otimiza simultaneamente filtros, joins e as agregações das CTEs.

```sql
-- Índices Recomendados
CREATE INDEX idx_nation_name ON nation (n_name);
CREATE INDEX idx_supplier_nationkey ON supplier (s_nationkey);
CREATE INDEX idx_orders_orderstatus ON orders (o_orderstatus);
CREATE INDEX idx_orders_orderkey ON orders (o_orderkey);
CREATE INDEX idx_lineitem_composite ON lineitem (l_orderkey, l_suppkey, l_receiptdate, l_commitdate);

WITH orders_with_multiple_suppliers AS (
    SELECT
        l_orderkey
    FROM
        lineitem
    GROUP BY
        l_orderkey
    HAVING
        COUNT(DISTINCT l_suppkey) > 1
),
orders_suppliers_with_late_others AS (
    SELECT DISTINCT
        l1.l_orderkey,
        l1.l_suppkey
    FROM
        lineitem l1
    JOIN
        lineitem l3 ON l1.l_orderkey = l3.l_orderkey
    WHERE
        l1.l_suppkey <> l3.l_suppkey
        AND l3.l_receiptdate > l3.l_commitdate
)
SELECT
    s.s_name,
    COUNT(*) AS numwait
FROM
    nation n
JOIN
    supplier s ON s.s_nationkey = n.n_nationkey
JOIN
    lineitem l1 ON s.s_suppkey = l1.l_suppkey
JOIN
    orders o ON l1.l_orderkey = o.o_orderkey
LEFT JOIN
    orders_suppliers_with_late_others oslo ON l1.l_orderkey = oslo.l_orderkey AND l1.l_suppkey = oslo.l_suppkey
WHERE
    n.n_name = 'SAUDI ARABIA'
    AND o.o_orderstatus = 'F'
    AND l1.l_receiptdate > l1.l_commitdate
    AND l1.l_orderkey IN (SELECT l_orderkey FROM orders_with_multiple_suppliers)
    AND oslo.l_orderkey IS NULL
GROUP BY
    s.s_name
ORDER BY
    numwait DESC,
    s_name
LIMIT 100;
```

---

## Comparação de Desempenho

X -> Não foi possível executar a consulta dentro do tempo limite estabelecido (20 minutos).

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | X              |                |                     |
| **Custo Inicial Estimado** | X              |                |                     |
| **Custo Total Estimado**   | X              |                |                     |
| **Linhas**                 | X              |                |                     |
| **Memória: Hit**           | X              |                |                     |
| **Memória: Read**          | X              |                |                     |
| **Memória: Dirtied**       | X              |                |                     |
| **Memória: Written**       | X              |                |                     |
| **Temp Read**              | X              |                |                     |
| **Temp Written**           | X              |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

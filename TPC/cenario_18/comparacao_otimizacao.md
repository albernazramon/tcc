# Comparação de Resultados: Cenário 18

## Queries Analisadas

### Pré-Otimização:

**Problema:** A consulta original possui uma subconsulta ineficiente (`IN` com `GROUP BY` e `HAVING`) que força a agregação total da tabela `lineitem` antes de filtrar os resultados. Além disso, a consulta principal recalcula redundantemente a soma de quantidades, gerando processamento extra. A falta de índices adequados para o `ORDER BY` e `LIMIT` obriga o PostgreSQL a realizar um `Sort` completo e custoso em um grande volume de dados intermediários.

```sql
-- using default substitutions


select
	c_name,
	c_custkey,
	o_orderkey,
	o_orderdate,
	o_totalprice,
	sum(l_quantity)
from
	customer,
	orders,
	lineitem
where
	o_orderkey in (
		select
			l_orderkey
		from
			lineitem
		group by
			l_orderkey having
				sum(l_quantity) > 300
	)
	and c_custkey = o_custkey
	and o_orderkey = l_orderkey
group by
	c_name,
	c_custkey,
	o_orderkey,
	o_orderdate,
	o_totalprice
order by
	o_totalprice desc,
	o_orderdate
limit 100;
```

### Pós-Otimização:

**Alterações:** A subconsulta foi refatorada para uma **CTE (Common Table Expression)** para pré-agregação e filtragem, eliminando a redundância de cálculos e simplificando o plano de execução. A consulta principal foi reescrita com **JOINs explícitos**. Foram recomendados índices compostos estratégicos: um em `lineitem` (`l_orderkey`, `l_quantity`) para acelerar a CTE, e outro em `orders` (`o_totalprice DESC`, `o_orderdate`, `o_custkey`, `o_orderkey`) para otimizar drasticamente o `ORDER BY` e o `LIMIT 100`, permitindo a recuperação direta das linhas ordenadas.

```sql
-- Índice para a CTE de agregação
CREATE INDEX IF NOT EXISTS idx_lineitem_orderkey_quantity ON public.lineitem (l_orderkey, l_quantity);

-- Índice composto para ORDER BY, LIMIT e junções
CREATE INDEX IF NOT EXISTS idx_orders_totalprice_date_custkey_orderkey ON public.orders (o_totalprice DESC, o_orderdate, o_custkey, o_orderkey);

-- Índices para chaves de junção
CREATE INDEX IF NOT EXISTS idx_orders_custkey ON public.orders (o_custkey);
CREATE INDEX IF NOT EXISTS idx_customer_custkey ON public.customer (c_custkey);

WITH OrderQuantities AS (
    SELECT
        l_orderkey,
        SUM(l_quantity) AS total_quantity_for_order
    FROM
        lineitem
    GROUP BY
        l_orderkey
    HAVING
        SUM(l_quantity) > 300
)
SELECT
    c.c_name,
    c.c_custkey,
    o.o_orderkey,
    o.o_orderdate,
    o.o_totalprice,
    oq.total_quantity_for_order
FROM
    customer c
JOIN
    orders o ON c.c_custkey = o.o_custkey
JOIN
    OrderQuantities oq ON o.o_orderkey = oq.l_orderkey
ORDER BY
    o.o_totalprice DESC,
    o.o_orderdate
LIMIT 100;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 667.961,19 ms  |                |                     |
| **Custo Inicial Estimado** | 12.857.429,83  |                |                     |
| **Custo Total Estimado**   | 12.857.432,83  |                |                     |
| **Linhas**                 | 100            |                |                     |
| **Memória: Hit**           | 308            |                |                     |
| **Memória: Read**          | 5.095.254      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 2.164.732      |                |                     |
| **Temp Written**           | 2.689.350      |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

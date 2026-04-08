# Comparação de Resultados: Cenário 22

## Queries Analisadas

### Pré-Otimização:

**Problema:** A consulta original apresenta redundância na filtragem da tabela `customer` tanto na consulta externa quanto na subconsulta de média, o que aumenta desnecessariamente o custo de CPU e I/O. Além disso, o uso da função `substring()` no `WHERE` torna a condição não-SARGable, impedindo o uso de índices B-tree padrão. A cláusula `NOT EXISTS` e o agrupamento em expressões calculadas também contribuem para a lentidão.

```sql
-- using default substitutions


select
	cntrycode,
	count(*) as numcust,
	sum(c_acctbal) as totacctbal
from
	(
		select
			substring(c_phone from 1 for 2) as cntrycode,
			c_acctbal
		from
			customer
		where
			substring(c_phone from 1 for 2) in
				('13', '31', '23', '29', '30', '18', '17')
			and c_acctbal > (
				select
					avg(c_acctbal)
				from
					customer
				where
					c_acctbal > 0.00
					and substring(c_phone from 1 for 2) in
						('13', '31', '23', '29', '30', '18', '17')
			)
			and not exists (
				select
					*
				from
					orders
				where
					o_custkey = c_custkey
			)
	) as custsale
group by
	cntrycode
order by
	cntrycode;
```

### Pós-Otimização:

**Alterações:** A consulta foi otimizada utilizando **CTEs (Common Table Expressions)** para pré-filtrar os clientes e calcular a média uma única vez, evitando varreduras redundantes. O `NOT EXISTS` foi substituído por um **LEFT JOIN / IS NULL**, oferecendo mais flexibilidade ao otimizador. Foi recomendada a criação de um **índice funcional e parcial** em `customer` (`substring(c_phone FROM 1 FOR 2)`, `c_acctbal`), tornando o filtro e o agrupamento muito mais eficientes.

```sql
-- Índice funcional e parcial na Tabela customer
CREATE INDEX idx_customer_cntrycode_acctbal
ON public.customer (substring(c_phone FROM 1 FOR 2), c_acctbal)
WHERE c_acctbal > 0.00;

-- Índice na Tabela orders
CREATE INDEX idx_orders_custkey ON public.orders (o_custkey);

WITH FilteredCustomers AS (
    SELECT
        c.c_custkey,
        substring(c.c_phone FROM 1 FOR 2) AS cntrycode,
        c.c_acctbal
    FROM
        customer c
    WHERE
        substring(c.c_phone FROM 1 FOR 2) IN ('13', '31', '23', '29', '30', '18', '17')
        AND c.c_acctbal > 0.00
),
AvgFilteredAcctBal AS (
    SELECT AVG(fc.c_acctbal) AS avg_bal
    FROM FilteredCustomers fc
)
SELECT
    fc.cntrycode,
    COUNT(fc.c_custkey) AS numcust,
    SUM(fc.c_acctbal) AS totacctbal
FROM
    FilteredCustomers fc
CROSS JOIN
    AvgFilteredAcctBal afab
LEFT JOIN
    orders o ON fc.c_custkey = o.o_custkey
WHERE
    fc.c_acctbal > afab.avg_bal
    AND o.o_orderkey IS NULL
GROUP BY
    fc.cntrycode
ORDER BY
    fc.cntrycode;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 4.545,01 ms    | 210.673,66 ms  |                     |
| **Custo Inicial Estimado** | 454.445,58     | 425.734,57     |                     |
| **Custo Total Estimado**   | 455.530,06     | 425.734,59     |                     |
| **Linhas**                 | 7666           | 1              |                     |
| **Memória: Hit**           | 304            | 670.066        |                     |
| **Memória: Read**          | 332.769        | 1.842.178      |                     |
| **Memória: Dirtied**       | -              | -              |                     |
| **Memória: Written**       | -              | 3              |                     |
| **Temp Read**              | -              | 1.118          |                     |
| **Temp Written**           | -              | -              |                     |

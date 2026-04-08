# Comparação de Resultados: Cenário 14

## Queries Analisadas

### Pré-Otimização:

**Problema:** A consulta original é lenta devido à provável ausência de índices em `l_shipdate`, `l_partkey`, `p_partkey` e `p_type`. Isso força o PostgreSQL a realizar varreduras sequenciais (`Seq Scan`) completas em tabelas grandes, resultando em junções ineficientes (`Hash Join` ou `Nested Loop` caros) e alto custo de I/O para filtrar o intervalo de datas.

```sql
-- using default substitutions


select
	100.00 * sum(case
		when p_type like 'PROMO%'
			then l_extendedprice * (1 - l_discount)
		else 0
	end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue
from
	lineitem,
	part
where
	l_partkey = p_partkey
	and l_shipdate >= date '1995-09-01'
	and l_shipdate < date '1995-09-01' + interval '1 month';
```

### Pós-Otimização:

**Alterações:** A consulta foi reescrita utilizando **INNER JOIN explícito** e a condição de data foi simplificada para `DATE '1995-10-01'`. A principal otimização é a criação de índices compostos: um em `lineitem` (`l_shipdate`, `l_partkey`) para acelerar o filtro de data e a junção, e outro em `part` (`p_partkey`, `p_type`) para permitir que a condição `p_type LIKE 'PROMO%'` seja verificada de forma eficiente, possivelmente via um **Index-Only Scan**.

```sql
-- Índice composto para lineitem
CREATE INDEX idx_lineitem_shipdate_partkey ON public.lineitem (l_shipdate, l_partkey);

-- Índice composto para part
CREATE INDEX idx_part_partkey_type ON public.part (p_partkey, p_type);

SELECT
    100.00 * SUM(CASE
        WHEN p.p_type LIKE 'PROMO%'
            THEN l.l_extendedprice * (1 - l.l_discount)
        ELSE 0
    END) / SUM(l.l_extendedprice * (1 - l.l_discount)) AS promo_revenue
FROM
    public.lineitem AS l
INNER JOIN
    public.part AS p ON l.l_partkey = p.p_partkey
WHERE
    l.l_shipdate >= DATE '1995-09-01'
    AND l.l_shipdate < DATE '1995-10-01';
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 18.268,47 ms   | 18.362,46 ms   |                     |
| **Custo Inicial Estimado** | 1.583.196,11   | 1.479.854,31   |                     |
| **Custo Total Estimado**   | 1.583.196,12   | 1.479.854,32   |                     |
| **Linhas**                 | 1              | 1              |                     |
| **Memória: Hit**           | -              | 1              |                     |
| **Memória: Read**          | 1.166.089      | 452.176        |                     |
| **Memória: Dirtied**       | -              | -              |                     |
| **Memória: Written**       | 15.172         | 3              |                     |
| **Temp Read**              | 14.827         | 14.825         |                     |
| **Temp Written**           | -              | -              |                     |

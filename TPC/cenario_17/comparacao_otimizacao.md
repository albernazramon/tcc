# Comparação de Resultados: Cenário 17

## Queries Analisadas

### Pré-Otimização:

**Problema:** O maior gargalo é uma subconsulta correlacionada no predicado `WHERE`, que obriga o PostgreSQL a recalcular a média de quantidade para cada linha processada pela consulta externa, gerando um custo proibitivo em tabelas grandes. Além disso, a falta de índices em `p_brand`, `p_container` e `l_partkey` resulta em varreduras sequenciais (`Seq Scan`) lentas e ineficientes.

```sql
-- using default substitutions


select
	sum(l_extendedprice) / 7.0 as avg_yearly
from
	lineitem,
	part
where
	p_partkey = l_partkey
	and p_brand = 'Brand#23'
	and p_container = 'MED BOX'
	and l_quantity < (
		select
			0.2 * avg(l_quantity)
		from
			lineitem
		where
			l_partkey = p_partkey
	);
```

### Pós-Otimização:

**Alterações:** A subconsulta correlacionada foi descorrelacionada através de uma **CTE (Common Table Expression)**, que pré-calcula o limite de quantidade para cada parte uma única vez. A consulta foi reescrita com **JOINs explícitos** para maior clareza. Foram recomendados índices compostos estratégicos em `part` (`p_brand`, `p_container`, `p_partkey`) e `lineitem` (`l_partkey`, `l_quantity`) para acelerar filtros, junções e a agregação da CTE.

```sql
-- Índice composto para a tabela part
CREATE INDEX idx_part_brand_container_partkey ON public.part (p_brand, p_container, p_partkey);

-- Índice composto para a tabela lineitem
CREATE INDEX idx_lineitem_partkey_quantity ON public.lineitem (l_partkey, l_quantity);

WITH PartAvgQuantity AS (
    SELECT
        l_partkey,
        0.2 * AVG(l_quantity) AS avg_qty_threshold
    FROM
        lineitem
    GROUP BY
        l_partkey
)
SELECT
    SUM(li.l_extendedprice) / 7.0 AS avg_yearly
FROM
    lineitem li
JOIN
    part p ON p.p_partkey = li.l_partkey
JOIN
    PartAvgQuantity paq ON li.l_partkey = paq.l_partkey
WHERE
    p.p_brand = 'Brand#23'
    AND p.p_container = 'MED BOX'
    AND li.l_quantity < paq.avg_qty_threshold;
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

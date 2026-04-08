# Comparação de Resultados: Cenário 4

## Queries Analisadas

### Pré-Otimização:

**Problema:** O uso de uma subconsulta correlacionada (`EXISTS`) obriga o PostgreSQL a executá-la para cada linha da tabela `orders` que atende ao filtro de data, gerando alto custo de CPU e I/O. Além disso, a falta de índices em `o_orderdate` e `l_orderkey` resulta em varreduras sequenciais ineficientes, e o agrupamento/ordenação final exige passos de `Sort` explícitos.

```sql
-- using default substitutions


select
	o_orderpriority,
	count(*) as order_count
from
	orders
where
	o_orderdate >= date '1993-07-01'
	and o_orderdate < date '1993-07-01' + interval '3 months'
	and exists (
		select
			*
		from
			lineitem
		where
			l_orderkey = o_orderkey
			and l_commitdate < l_receiptdate
	)
group by
	o_orderpriority
order by
	o_orderpriority;
```

### Pós-Otimização:

**Alterações:** A subconsulta correlacionada foi substituída por um **INNER JOIN com uma subconsulta DISTINCT**, permitindo que o filtro em `lineitem` seja executado apenas uma vez e possibilitando estratégias de junção mais eficientes (Hash ou Merge Join). Foram recomendados índices compostos: um em `lineitem` para acelerar o filtro interno e o `DISTINCT`, e um em `orders` (`o_orderdate`, `o_orderpriority`, `o_orderkey`) que otimiza simultaneamente o filtro de data, a junção e elimina a necessidade de ordenação explícita para o `GROUP BY` e `ORDER BY`.

```sql
-- Índice para a tabela lineitem
CREATE INDEX idx_lineitem_commit_receipt_orderkey ON lineitem (l_commitdate, l_receiptdate, l_orderkey);

-- Índice para a tabela orders
CREATE INDEX idx_orders_date_priority_key ON orders (o_orderdate, o_orderpriority, o_orderkey);

SELECT
    o.o_orderpriority,
    COUNT(o.o_orderkey) AS order_count
FROM
    orders o
JOIN (
    SELECT DISTINCT l_orderkey
    FROM lineitem
    WHERE l_commitdate < l_receiptdate
) AS filtered_lineitems ON o.o_orderkey = filtered_lineitems.l_orderkey
WHERE
    o.o_orderdate >= DATE '1993-07-01'
    AND o.o_orderdate < DATE '1993-07-01' + INTERVAL '3 months'
GROUP BY
    o.o_orderpriority
ORDER BY
    o.o_orderpriority;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 33.742,09 ms   | 75.264,24 ms   |                     |
| **Custo Inicial Estimado** | 1.966.862,42   | 2.150.110,62   |                     |
| **Custo Total Estimado**   | 1.966.917,66   | 2.150.221,72   |                     |
| **Linhas**                 | 5              | 5              |                     |
| **Memória: Hit**           | 14             | 3.701          |                     |
| **Memória: Read**          | 1.386.331      | 1.127.965      |                     |
| **Memória: Dirtied**       | -              | -              |                     |
| **Memória: Written**       | 116.644        | 486.505        |                     |
| **Temp Read**              | 115.471        | 379.191        |                     |
| **Temp Written**           | -              | -              |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

# Comparação de Resultados: Cenário 12

## Queries Analisadas

### Pré-Otimização:

**Problema:** A ausência de índices nas tabelas `orders` e `lineitem` força o PostgreSQL a realizar varreduras sequenciais (`Seq Scan`) completas, o que é extremamente ineficiente para tabelas grandes. Filtros seletivos de data e modo de envio, além da junção entre as tabelas, consomem excessivamente recursos de I/O e CPU, resultando em ordenações explícitas custosas para o `GROUP BY` e `ORDER BY`.

```sql
-- using default substitutions


select
	l_shipmode,
	sum(case
		when o_orderpriority = '1-URGENT'
			or o_orderpriority = '2-HIGH'
			then 1
		else 0
	end) as high_line_count,
	sum(case
		when o_orderpriority <> '1-URGENT'
			and o_orderpriority <> '2-HIGH'
			then 1
		else 0
	end) as low_line_count
from
	orders,
	lineitem
where
	o_orderkey = l_orderkey
	and l_shipmode in ('MAIL', 'SHIP')
	and l_commitdate < l_receiptdate
	and l_shipdate < l_commitdate
	and l_receiptdate >= date '1994-01-01'
	and l_receiptdate < date '1994-01-01' + interval '1 year'
group by
	l_shipmode
order by
	l_shipmode;
```

### Pós-Otimização:

**Alterações:** A otimização foca na criação de índices estratégicos. Foi sugerido um índice em `orders.o_orderkey` para otimizar o `JOIN`, e um **índice composto** em `lineitem` (`l_shipmode`, `l_receiptdate`, `l_commitdate`, `l_shipdate`, `l_orderkey`). Esse índice composto permite filtrar eficientemente por modo de envio e data, além de possibilitar que o agrupamento e a ordenação sejam satisfeitos diretamente pela estrutura do índice, eliminando passos de `Sort` explícitos.

```sql
-- Índice para otimizar o JOIN
CREATE INDEX idx_orders_o_orderkey ON public.orders (o_orderkey);

-- Índice composto para filtros, JOIN e ordenação
CREATE INDEX idx_lineitem_optimized ON public.lineitem (l_shipmode, l_receiptdate, l_commitdate, l_shipdate, l_orderkey);

select
	l_shipmode,
	sum(case
		when o_orderpriority = '1-URGENT'
			or o_orderpriority = '2-HIGH'
			then 1
		else 0
	end) as high_line_count,
	sum(case
		when o_orderpriority <> '1-URGENT'
			and o_orderpriority <> '2-HIGH'
			then 1
		else 0
	end) as low_line_count
from
	orders,
	lineitem
where
	o_orderkey = l_orderkey
	and l_shipmode in ('MAIL', 'SHIP')
	and l_commitdate < l_receiptdate
	and l_shipdate < l_commitdate
	and l_receiptdate >= date '1994-01-01'
	and l_receiptdate < date '1994-01-01' + interval '1 year'
group by
	l_shipmode
order by
	l_shipmode;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 100.335,34 ms  |                |                     |
| **Custo Inicial Estimado** | 4.362.218,33   |                |                     |
| **Custo Total Estimado**   | 4.367.077,82   |                |                     |
| **Linhas**                 | 7              |                |                     |
| **Memória: Hit**           | 14             |                |                     |
| **Memória: Read**          | 2.773.065      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 152.222        |                |                     |
| **Temp Written**           | 153.225        |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

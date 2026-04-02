# Comparação de Resultados: Cenário 12

## Queries Analisadas

### Pré-Otimização: TODO

**Problema:** TODO

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

### Pós-Otimização: TODO

**Alterações:** TODO

```sql
_scripts here_
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

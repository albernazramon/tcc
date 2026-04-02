# Comparação de Resultados: Cenário 18

## Queries Analisadas

### Pré-Otimização: TODO

**Problema:** TODO

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

### Pós-Otimização: TODO

**Alterações:** TODO

```sql
_scripts here_
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

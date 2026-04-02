# Comparação de Resultados: Cenário 5

## Queries Analisadas

### Pré-Otimização: TODO

**Problema:** TODO

```sql
-- using default substitutions


select
	n_name,
	sum(l_extendedprice * (1 - l_discount)) as revenue
from
	customer,
	orders,
	lineitem,
	supplier,
	nation,
	region
where
	c_custkey = o_custkey
	and l_orderkey = o_orderkey
	and l_suppkey = s_suppkey
	and c_nationkey = s_nationkey
	and s_nationkey = n_nationkey
	and n_regionkey = r_regionkey
	and r_name = 'ASIA'
	and o_orderdate >= date '1994-01-01'
	and o_orderdate < date '1994-01-01' + interval '1 year'
group by
	n_name
order by
	revenue desc;
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
| **Tempo de Execução**      | 85.487,27 ms   |                |                     |
| **Custo Inicial Estimado** | 4.141.853,84   |                |                     |
| **Custo Total Estimado**   | 4.141.853,90   |                |                     |
| **Linhas**                 | 25             |                |                     |
| **Memória: Hit**           | 21             |                |                     |
| **Memória: Read**          | 2.849.349      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 279.294        |                |                     |
| **Temp Written**           | 279.892        |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

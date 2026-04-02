# Comparação de Resultados: Cenário 14

## Queries Analisadas

### Pré-Otimização: TODO

**Problema:** TODO

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

### Pós-Otimização: TODO

**Alterações:** TODO

```sql
_scripts here_
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 66.854,92 ms   |                |                     |
| **Custo Inicial Estimado** | 3.164.958,41   |                |                     |
| **Custo Total Estimado**   | 3.164.958,42   |                |                     |
| **Linhas**                 | 1              |                |                     |
| **Memória: Hit**           | -              |                |                     |
| **Memória: Read**          | 2.332.550      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 30.006         |                |                     |
| **Temp Written**           | 30.732         |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

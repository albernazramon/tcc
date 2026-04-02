# Comparação de Resultados: Cenário 17

## Queries Analisadas

### Pré-Otimização: TODO

**Problema:** TODO

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

### Pós-Otimização: TODO

**Alterações:** TODO

```sql
_scripts here_
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

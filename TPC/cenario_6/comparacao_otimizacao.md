# Comparação de Resultados: Cenário 6

## Queries Analisadas

### Pré-Otimização: TODO

**Problema:** TODO

```sql
-- using default substitutions


select
	sum(l_extendedprice * l_discount) as revenue
from
	lineitem
where
	l_shipdate >= date '1994-01-01'
	and l_shipdate < date '1994-01-01' + interval '1 year'
	and l_discount between .06 - 0.01 and .06 + 0.01
	and l_quantity < 24;
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
| **Tempo de Execução**      | 57.891,58 ms   |                |                     |
| **Custo Inicial Estimado** | 3.381.417,81   |                |                     |
| **Custo Total Estimado**   | 3.381.417,82   |                |                     |
| **Linhas**                 | 1              |                |                     |
| **Memória: Hit**           | -              |                |                     |
| **Memória: Read**          | 2.250.632      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | -              |                |                     |
| **Temp Written**           | -              |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

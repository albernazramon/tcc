# Comparação de Resultados: Cenário 11

## Queries Analisadas

### Pré-Otimização:

**Problema:** O principal problema é a execução redundante da mesma lógica de junção e agregação tanto na consulta principal quanto na subconsulta da cláusula `HAVING`. Isso obriga o PostgreSQL a processar as tabelas `partsupp`, `supplier` e `nation` duas vezes, gerando um custo computacional e de I/O desnecessário. Além disso, a ordenação final por um valor agregado exige um passo de `Sort` explícito.

```sql
-- using default substitutions


select
	ps_partkey,
	sum(ps_supplycost * ps_availqty) as value
from
	partsupp,
	supplier,
	nation
where
	ps_suppkey = s_suppkey
	and s_nationkey = n_nationkey
	and n_name = 'GERMANY'
group by
	ps_partkey having
		sum(ps_supplycost * ps_availqty) > (
			select
				sum(ps_supplycost * ps_availqty) * 0.0001000000
			from
				partsupp,
				supplier,
				nation
			where
				ps_suppkey = s_suppkey
				and s_nationkey = n_nationkey
				and n_name = 'GERMANY'
		)
order by
	value desc;
```

### Pós-Otimização:

**Alterações:** A redundância foi eliminada através do uso de uma **função de janela (`SUM(...) OVER ()`)** dentro de uma subconsulta derivada. Isso permite que o total geral necessário para o filtro seja calculado uma única vez sobre os resultados já agregados, evitando a reexecução completa dos joins. Foram recomendados índices estratégicos para acelerar a filtragem inicial e as junções, incluindo um **índice de cobertura (`INCLUDE`)** em `partsupp` para possibilitar um `Index-Only Scan`.

```sql
-- Índices Recomendados
CREATE INDEX idx_nation_name ON nation (n_name);
CREATE INDEX idx_nation_nkey ON nation (n_nationkey);
CREATE INDEX idx_supplier_nkey_skey ON supplier (s_nationkey, s_suppkey);
CREATE INDEX idx_partsupp_skey_pkey_include ON partsupp (ps_suppkey, ps_partkey) INCLUDE (ps_supplycost, ps_availqty);

SELECT
    ps_partkey,
    value
FROM (
    SELECT
        ps_partkey,
        sum(ps_supplycost * ps_availqty) AS value,
        sum(sum(ps_supplycost * ps_availqty)) OVER () AS total_germany_value
    FROM
        partsupp
    JOIN
        supplier ON ps_suppkey = s_suppkey
    JOIN
        nation ON s_nationkey = n_nationkey
    WHERE
        n_name = 'GERMANY'
    GROUP BY
        ps_partkey
) AS grouped_values_with_total
WHERE
    value > total_germany_value * 0.0001000000
ORDER BY
    value DESC;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 14.794,15 ms   |                |                     |
| **Custo Inicial Estimado** | 1.036.997,66   |                |                     |
| **Custo Total Estimado**   | 1.037.414,47   |                |                     |
| **Linhas**                 | 166.725        |                |                     |
| **Memória: Hit**           | 586            |                |                     |
| **Memória: Read**          | 708.453        |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 2.062          |                |                     |
| **Temp Written**           | 2.068          |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

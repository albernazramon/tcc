# Comparação de Resultados: Cenário 20

## Queries Analisadas

### Pré-Otimização:

**Problema:** O maior entrave é uma subconsulta escalar correlacionada dentro da cláusula `WHERE` da tabela `partsupp`, que é reexecutada para cada linha, gerando um custo massivo de CPU e I/O. Além disso, a estrutura de múltiplas subconsultas aninhadas com `IN` e a falta de índices em `p_name` (filtro `LIKE 'forest%'`) e chaves estrangeiras forçam varreduras sequenciais e junções ineficientes.

```sql
-- using default substitutions


select
	s_name,
	s_address
from
	supplier,
	nation
where
	s_suppkey in (
		select
			ps_suppkey
		from
			partsupp
		where
			ps_partkey in (
				select
					p_partkey
				from
					part
				where
					p_name like 'forest%'
			)
			and ps_availqty > (
				select
					0.5 * sum(l_quantity)
				from
					lineitem
				where
					l_partkey = ps_partkey
					and l_suppkey = ps_suppkey
					and l_shipdate >= date '1994-01-01'
					and l_shipdate < date '1994-01-01' + interval '1 year'
			)
	)
	and s_nationkey = n_nationkey
	and n_name = 'CANADA'
order by
	s_name;
```

### Pós-Otimização:

**Alterações:** As subconsultas correlacionadas e aninhadas foram eliminadas e substituídas por uma **subconsulta derivada agregada (`li_agg`)** e **INNER JOINs explícitos**, transformando operações repetitivas em uma agregação única e junções eficientes. Foram recomendados índices estratégicos em `part.p_name` (para o filtro `LIKE`), `lineitem` (índice composto para a agregação), e em todas as chaves estrangeiras, permitindo que o PostgreSQL utilize `Index Scans` e algoritmos de junção mais rápidos.

```sql
-- Índices Recomendados
CREATE INDEX idx_part_p_name ON public.part (p_name);
CREATE INDEX idx_nation_n_name ON public.nation (n_name);
CREATE INDEX idx_supplier_s_nationkey ON public.supplier (s_nationkey);
CREATE INDEX idx_supplier_s_suppkey ON public.supplier (s_suppkey);
CREATE INDEX idx_partsupp_ps_suppkey_ps_partkey ON public.partsupp (ps_suppkey, ps_partkey);
CREATE INDEX idx_lineitem_shipdate_partkey_suppkey ON public.lineitem (l_shipdate, l_partkey, l_suppkey);

SELECT
    s.s_name,
    s.s_address
FROM
    supplier s
JOIN
    nation n ON s.s_nationkey = n.n_nationkey
JOIN
    partsupp ps ON s.s_suppkey = ps.ps_suppkey
JOIN
    part p ON ps.ps_partkey = p.p_partkey
JOIN (
    SELECT
        l_partkey,
        l_suppkey,
        0.5 * SUM(l_quantity) AS half_sum_quantity
    FROM
        lineitem
    WHERE
        l_shipdate >= DATE '1994-01-01'
        AND l_shipdate < DATE '1995-01-01'
    GROUP BY
        l_partkey,
        l_suppkey
) AS li_agg ON ps.ps_partkey = li_agg.l_partkey AND ps.ps_suppkey = li_agg.l_suppkey
WHERE
    n.n_name = 'CANADA'
    AND p.p_name LIKE 'forest%'
    AND ps.ps_availqty > li_agg.half_sum_quantity
ORDER BY
    s.s_name;
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

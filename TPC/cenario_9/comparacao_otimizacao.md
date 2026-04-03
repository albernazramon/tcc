# Comparação de Resultados: Cenário 9

## Queries Analisadas

### Pré-Otimização:

**Problema:** O maior gargalo é o filtro `p_name LIKE '%green%'`, que impede o uso de índices B-tree padrão e força um `Seq Scan` em toda a tabela `part`. Além disso, a ausência de índices em chaves estrangeiras dificulta as junções entre as seis tabelas envolvidas, e o agrupamento/ordenação final exige processamento intensivo de memória e CPU (provável `Hash Aggregate` e `Sort` explícito).

```sql
-- using default substitutions


select
	nation,
	o_year,
	sum(amount) as sum_profit
from
	(
		select
			n_name as nation,
			extract(year from o_orderdate) as o_year,
			l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount
		from
			part,
			supplier,
			lineitem,
			partsupp,
			orders,
			nation
		where
			s_suppkey = l_suppkey
			and ps_suppkey = l_suppkey
			and ps_partkey = l_partkey
			and p_partkey = l_partkey
			and o_orderkey = l_orderkey
			and s_nationkey = n_nationkey
			and p_name like '%green%'
	) as profit
group by
	nation,
	o_year
order by
	nation,
	o_year desc;
```

### Pós-Otimização:

**Alterações:** A consulta foi reescrita com `JOIN`s explícitos para maior clareza. A otimização principal consiste na criação de um **índice GIN com pg_trgm** na coluna `p_name`, permitindo buscas eficientes com curingas iniciais. Também foram sugeridos índices B-tree em todas as chaves estrangeiras (`l_partkey`, `l_suppkey`, `o_orderkey`, etc.) e um índice de expressão para `EXTRACT(YEAR FROM o_orderdate)`, reduzindo drasticamente o volume de dados processados e agilizando as junções e a agregação.

```sql
-- Habilita a extensão pg_trgm para buscas de texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_part_p_name_trgm ON public.part USING GIN (p_name gin_trgm_ops);

-- Índices para otimizar as junções (chaves estrangeiras)
CREATE INDEX idx_lineitem_partkey ON public.lineitem (l_partkey);
CREATE INDEX idx_lineitem_suppkey ON public.lineitem (l_suppkey);
CREATE INDEX idx_lineitem_orderkey ON public.lineitem (l_orderkey);
CREATE INDEX idx_supplier_nationkey ON public.supplier (s_nationkey);

-- Índices para auxiliar no agrupamento e ordenação
CREATE INDEX idx_orders_o_orderdate_year ON public.orders (EXTRACT(YEAR FROM o_orderdate));
CREATE INDEX idx_nation_name ON public.nation (n_name);

SELECT
    n.n_name AS nation,
    EXTRACT(YEAR FROM o.o_orderdate) AS o_year,
    SUM(l.l_extendedprice * (1 - l.l_discount) - ps.ps_supplycost * l.l_quantity) AS sum_profit
FROM
    part AS p
JOIN
    lineitem AS l ON p.p_partkey = l.l_partkey
JOIN
    partsupp AS ps ON l.l_partkey = ps.ps_partkey AND l.l_suppkey = ps.ps_suppkey
JOIN
    supplier AS s ON l.l_suppkey = s.s_suppkey
JOIN
    orders AS o ON l.l_orderkey = o.o_orderkey
JOIN
    nation AS n ON s.s_nationkey = n.n_nationkey
WHERE
    p.p_name LIKE '%green%'
GROUP BY
    n.n_name,
    EXTRACT(YEAR FROM o.o_orderdate)
ORDER BY
    n.n_name,
    EXTRACT(YEAR FROM o.o_orderdate) DESC;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 192.849,55 ms  |                |                     |
| **Custo Inicial Estimado** | 4.447.997,58   |                |                     |
| **Custo Total Estimado**   | 4.448.023,65   |                |                     |
| **Linhas**                 | 175            |                |                     |
| **Memória: Hit**           | 30             |                |                     |
| **Memória: Read**          | 3.209.492      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 876.110        |                |                     |
| **Temp Written**           | 879.157        |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

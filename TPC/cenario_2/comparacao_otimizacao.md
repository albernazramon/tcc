# Comparação de Resultados: Cenário 2

## Queries Analisadas

### Pré-Otimização:

**Problema:** O principal gargalo é uma subconsulta correlacionada no `WHERE` que é reexecutada para cada linha da consulta externa, gerando alto custo computacional. Além disso, a condição `LIKE '%BRASS'` impede o uso eficiente de índices B-tree (não SARGable), forçando varreduras sequenciais. A ordenação complexa com `ORDER BY` e `LIMIT` também exige um `Sort` explícito custoso em grandes volumes de dados.

```sql
-- using default substitutions


select
	s_acctbal,
	s_name,
	n_name,
	p_partkey,
	p_mfgr,
	s_address,
	s_phone,
	s_comment
from
	part,
	supplier,
	partsupp,
	nation,
	region
where
	p_partkey = ps_partkey
	and s_suppkey = ps_suppkey
	and p_size = 15
	and p_type like '%BRASS'
	and s_nationkey = n_nationkey
	and n_regionkey = r_regionkey
	and r_name = 'EUROPE'
	and ps_supplycost = (
		select
			min(ps_supplycost)
		from
			partsupp,
			supplier,
			nation,
			region
		where
			p_partkey = ps_partkey
			and s_suppkey = ps_suppkey
			and s_nationkey = n_nationkey
			and n_regionkey = r_regionkey
			and r_name = 'EUROPE'
	)
order by
	s_acctbal desc,
	n_name,
	s_name,
	p_partkey
limit 100;
```

### Pós-Otimização:

**Alterações:** A subconsulta correlacionada foi substituída por uma **CTE (Common Table Expression)** para pré-calcular os valores mínimos, transformando execuções repetitivas em uma junção única e eficiente. Foi recomendada a criação de um **índice GIN com pg_trgm** para otimizar o filtro `LIKE '%BRASS'`. Índices compostos e específicos para ordenação (`s_acctbal`, `s_name`) foram sugeridos para permitir que o PostgreSQL recupere as linhas já ordenadas, otimizando o `LIMIT 100` e evitando ordenações completas em memória ou disco.

```sql
-- Habilita a extensão pg_trgm para índices de texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Índices para chaves estrangeiras e condições de junção/filtro
CREATE INDEX IF NOT EXISTS idx_supplier_nationkey ON public.supplier (s_nationkey);
CREATE INDEX IF NOT EXISTS idx_nation_regionkey ON public.nation (n_regionkey);
CREATE INDEX IF NOT EXISTS idx_region_rname ON public.region (r_name);
CREATE INDEX IF NOT EXISTS idx_part_psize ON public.part (p_size);

-- Índice para a CTE MinSupplyCost e condição de junção
CREATE INDEX IF NOT EXISTS idx_partsupp_partkey_supplycost ON public.partsupp (ps_partkey, ps_supplycost);

-- Índices para a cláusula ORDER BY e LIMIT
CREATE INDEX IF NOT EXISTS idx_supplier_acctbal_name ON public.supplier (s_acctbal DESC, s_name ASC);
CREATE INDEX IF NOT EXISTS idx_nation_name ON public.nation (n_name ASC);
CREATE INDEX IF NOT EXISTS idx_part_partkey ON public.part (p_partkey ASC);

-- Índice para a condição LIKE '%BRASS' (requer a extensão pg_trgm)
CREATE INDEX IF NOT EXISTS idx_part_ptype_trgm ON public.part USING GIN (p_type gin_trgm_ops);

WITH MinSupplyCost AS (
    SELECT
        ps.ps_partkey,
        MIN(ps.ps_supplycost) AS min_ps_supplycost_europe
    FROM
        public.partsupp ps
    JOIN
        public.supplier s ON ps.ps_suppkey = s.s_suppkey
    JOIN
        public.nation n ON s.s_nationkey = n.n_nationkey
    JOIN
        public.region r ON n.n_regionkey = r.r_regionkey
    WHERE
        r.r_name = 'EUROPE'
    GROUP BY
        ps.ps_partkey
)
SELECT
    s.s_acctbal,
    s.s_name,
    n.n_name,
    p.p_partkey,
    p.p_mfgr,
    s.s_address,
    s.s_phone,
    s.s_comment
FROM
    public.part p
JOIN
    public.partsupp ps ON p.p_partkey = ps.ps_partkey
JOIN
    public.supplier s ON s.s_suppkey = ps.ps_suppkey
JOIN
    public.nation n ON s.s_nationkey = n.n_nationkey
JOIN
    public.region r ON n.n_regionkey = r.r_regionkey
JOIN
    MinSupplyCost msc ON ps.ps_partkey = msc.ps_partkey AND ps.ps_supplycost = msc.min_ps_supplycost_europe
WHERE
    p.p_size = 15
    AND p.p_type LIKE '%BRASS'
    AND r.r_name = 'EUROPE'
ORDER BY
    s.s_acctbal DESC,
    n.n_name ASC,
    s.s_name ASC,
    p.p_partkey ASC
LIMIT 100;
```

---

## Comparação de Desempenho

X -> Não foi possível executar a consulta dentro do tempo limite estabelecido (20 minutos).

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | X              | 8.720,13 ms    |                     |
| **Custo Inicial Estimado** | X              | 460.702,29     |                     |
| **Custo Total Estimado**   | X              | 460.703,48     |                     |
| **Linhas**                 | X              | 1              |                     |
| **Memória: Hit**           | X              | 62.239         |                     |
| **Memória: Read**          | X              | 366.046        |                     |
| **Memória: Dirtied**       | X              | -              |                     |
| **Memória: Written**       | X              | 22.712         |                     |
| **Temp Read**              | X              | 11.538         |                     |
| **Temp Written**           | X              | -              |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

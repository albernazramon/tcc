# Comparação de Resultados: Cenário 16

## Queries Analisadas

### Pré-Otimização:

**Problema:** O maior gargalo é a cláusula `NOT IN` com um filtro `LIKE '%Customer%Complaints%'`, que impede o uso de índices B-tree e força um `Seq Scan` completo na tabela `supplier`. Além disso, a agregação `COUNT(DISTINCT)` impede a paralelização, e a falta de índices adequados em `part` para os filtros de marca, tipo e tamanho resulta em processamento ineficiente de grandes volumes de dados.

```sql
-- using default substitutions


select
	p_brand,
	p_type,
	p_size,
	count(distinct ps_suppkey) as supplier_cnt
from
	partsupp,
	part
where
	p_partkey = ps_partkey
	and p_brand <> 'Brand#45'
	and p_type not like 'MEDIUM POLISHED%'
	and p_size in (49, 14, 23, 45, 19, 3, 36, 9)
	and ps_suppkey not in (
		select
			s_suppkey
		from
			supplier
		where
			s_comment like '%Customer%Complaints%'
	)
group by
	p_brand,
	p_type,
	p_size
order by
	supplier_cnt desc,
	p_brand,
	p_type,
	p_size;
```

### Pós-Otimização:

**Alterações:** A subconsulta `NOT IN` foi substituída por uma **CTE** e um **LEFT JOIN / IS NULL**, técnica geralmente mais eficiente no PostgreSQL. Foi recomendada a criação de um **índice GIN com pg_trgm** na coluna `s_comment` para otimizar o filtro `LIKE` com curinga inicial. Também foram sugeridos índices compostos em `part` (`p_brand`, `p_type`, `p_size`) para acelerar simultaneamente filtros, agrupamento e ordenação, além de índices em chaves estrangeiras para otimizar o `JOIN` e o `DISTINCT`.

```sql
-- Habilita a extensão pg_trgm e cria o índice GIN
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_supplier_s_comment_trgm ON public.supplier USING GIN (s_comment gin_trgm_ops);

-- Índices adicionais para otimização
CREATE INDEX idx_part_brand_type_size ON public.part (p_brand, p_type, p_size);
CREATE INDEX idx_partsupp_suppkey ON public.partsupp (ps_suppkey);

WITH problematic_suppliers AS (
    SELECT
        s_suppkey
    FROM
        supplier
    WHERE
        s_comment LIKE '%Customer%Complaints%'
)
SELECT
    p.p_brand,
    p.p_type,
    p.p_size,
    count(DISTINCT ps.ps_suppkey) AS supplier_cnt
FROM
    part p
JOIN
    partsupp ps ON p.p_partkey = ps.ps_partkey
LEFT JOIN
    problematic_suppliers psup ON ps.ps_suppkey = psup.s_suppkey
WHERE
    p.p_brand <> 'Brand#45'
    AND p.p_type NOT LIKE 'MEDIUM POLISHED%'
    AND p.p_size IN (49, 14, 23, 45, 19, 3, 36, 9)
    AND psup.s_suppkey IS NULL
GROUP BY
    p.p_brand,
    p.p_type,
    p.p_size
ORDER BY
    supplier_cnt DESC,
    p.p_brand,
    p.p_type,
    p.p_size;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 7.660,41 ms    | 7.500,37 ms    |                     |
| **Custo Inicial Estimado** | 430.509,92     | 533.578,52     |                     |
| **Custo Total Estimado**   | 430.894,44     | 533.960,07     |                     |
| **Linhas**                 | 153810         | 152618         |                     |
| **Memória: Hit**           | 4.465          | 291            |                     |
| **Memória: Read**          | 218.225        | 216.371        |                     |
| **Memória: Dirtied**       | -              | -              |                     |
| **Memória: Written**       | 36.653         | 36.672         |                     |
| **Temp Read**              | 36.610         | 36.622         |                     |
| **Temp Written**           | -              | -              |                     |

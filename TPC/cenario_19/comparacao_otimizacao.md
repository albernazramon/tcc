# Comparação de Resultados: Cenário 19

## Queries Analisadas

### Pré-Otimização:

**Problema:** A consulta original utiliza uma cláusula `OR` complexa abrangendo múltiplas colunas e tabelas, o que dificulta o uso eficiente de índices compostos e obriga o PostgreSQL a realizar varreduras sequenciais (`Seq Scan`) ou `Bitmap Heap Scans` custosos. Além disso, a junção `p_partkey = l_partkey` é avaliada repetidamente dentro de cada bloco `OR`, gerando redundância e impedindo um plano de execução coeso e otimizado.

```sql
-- using default substitutions


select
	sum(l_extendedprice* (1 - l_discount)) as revenue
from
	lineitem,
	part
where
	(
		p_partkey = l_partkey
		and p_brand = 'Brand#12'
		and p_container in ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG')
		and l_quantity >= 1 and l_quantity <= 1 + 10
		and p_size between 1 and 5
		and l_shipmode in ('AIR', 'AIR REG')
		and l_shipinstruct = 'DELIVER IN PERSON'
	)
	or
	(
		p_partkey = l_partkey
		and p_brand = 'Brand#23'
		and p_container in ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
		and l_quantity >= 10 and l_quantity <= 10 + 10
		and p_size between 1 and 10
		and l_shipmode in ('AIR', 'AIR REG')
		and l_shipinstruct = 'DELIVER IN PERSON'
	)
	or
	(
		p_partkey = l_partkey
		and p_brand = 'Brand#34'
		and p_container in ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
		and l_quantity >= 20 and l_quantity <= 20 + 10
		and p_size between 1 and 15
		and l_shipmode in ('AIR', 'AIR REG')
		and l_shipinstruct = 'DELIVER IN PERSON'
	);
```

### Pós-Otimização:

**Alterações:** A cláusula `OR` foi refatorada em uma estrutura de **UNION ALL**, permitindo que o PostgreSQL otimize cada subconsulta de forma independente com seus próprios filtros `AND`. Foi recomendado um **índice composto** para a tabela `part` e um **índice de cobertura (covering index)** para a tabela `lineitem` (`l_shipinstruct`, `l_shipmode`, `l_quantity`, `l_partkey` incluindo preço e desconto), possibilitando um **Index-Only Scan** e reduzindo drasticamente o custo de I/O e CPU.

```sql
-- Índice composto para a tabela part
CREATE INDEX idx_part_brand_container_size_partkey ON public.part (p_brand, p_container, p_size, p_partkey);

-- Índice de cobertura para a tabela lineitem
CREATE INDEX idx_lineitem_ship_qty_partkey_covering
ON public.lineitem (l_shipinstruct, l_shipmode, l_quantity, l_partkey)
INCLUDE (l_extendedprice, l_discount);

SELECT SUM(revenue) AS revenue
FROM (
    SELECT
        l.l_extendedprice * (1 - l.l_discount) AS revenue
    FROM
        lineitem l
    JOIN
        part p ON p.p_partkey = l.l_partkey
    WHERE
        p.p_brand = 'Brand#12'
        AND p.p_container IN ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG')
        AND l.l_quantity BETWEEN 1 AND 11
        AND p.p_size BETWEEN 1 AND 5
        AND l.l_shipmode IN ('AIR', 'AIR REG')
        AND l.l_shipinstruct = 'DELIVER IN PERSON'
    UNION ALL
    SELECT
        l.l_extendedprice * (1 - l.l_discount) AS revenue
    FROM
        lineitem l
    JOIN
        part p ON p.p_partkey = l.l_partkey
    WHERE
        p.p_brand = 'Brand#23'
        AND p.p_container IN ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
        AND l.l_quantity BETWEEN 10 AND 20
        AND p.p_size BETWEEN 1 AND 10
        AND l.l_shipmode IN ('AIR', 'AIR REG')
        AND l.l_shipinstruct = 'DELIVER IN PERSON'
    UNION ALL
    SELECT
        l.l_extendedprice * (1 - l.l_discount) AS revenue
    FROM
        lineitem l
    JOIN
        part p ON p.p_partkey = l.l_partkey
    WHERE
        p.p_brand = 'Brand#34'
        AND p.p_container IN ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
        AND l.l_quantity BETWEEN 20 AND 30
        AND p.p_size BETWEEN 1 AND 15
        AND l.l_shipmode IN ('AIR', 'AIR REG')
        AND l.l_shipinstruct = 'DELIVER IN PERSON'
) AS subquery_revenue;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 16.988,14 ms   | 1.403,62 ms    |                     |
| **Custo Inicial Estimado** | 1.954.023,41   | 84.713,74      |                     |
| **Custo Total Estimado**   | 1.954.023,42   | 84.713,75      |                     |
| **Linhas**                 | 1              | 1              |                     |
| **Memória: Hit**           | -              | 917.721        |                     |
| **Memória: Read**          | 1.166.089      | 15.874         |                     |
| **Memória: Dirtied**       | -              | -              |                     |
| **Memória: Written**       | -              | -              |                     |
| **Temp Read**              | -              | -              |                     |
| **Temp Written**           | -              | -              |                     |

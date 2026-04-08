# Comparação de Resultados: Cenário 13

## Queries Analisadas

### Pré-Otimização:

**Problema:** A condição `NOT LIKE '%special%requests%'` é o principal ponto de lentidão, pois padrões que iniciam com curinga (`%`) impedem o uso de índices B-tree padrão, forçando varreduras sequenciais (`Seq Scan`) completas em `orders`. Além disso, a ausência de índice na chave estrangeira `o_custkey` prejudica a eficiência da junção, e as múltiplas etapas de agregação e ordenação exigem processamento intensivo de recursos.

```sql
-- using default substitutions


select
	c_count,
	count(*) as custdist
from
	(
		select
			c_custkey,
			count(o_orderkey) as c_count
		from
			customer left outer join orders on
				c_custkey = o_custkey
				and o_comment not like '%special%requests%'
		group by
			c_custkey
	) as c_orders
group by
	c_count
order by
	custdist desc,
	c_count desc;
```

### Pós-Otimização:

**Alterações:** Foi recomendada a criação de um **índice GIN com pg_trgm** na coluna `o_comment`, permitindo acelerar buscas de texto com padrões `LIKE`. Além disso, a criação de um índice em `orders.o_custkey` otimiza a junção entre `customer` e `orders`, permitindo que o planejador escolha planos de junção mais eficientes (como `Nested Loop Join` ou `Merge Join`) e reduza drasticamente o custo de I/O.

```sql
-- Habilita a extensão pg_trgm e cria o índice GIN
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_orders_o_comment_trgm ON orders USING GIN (o_comment gin_trgm_ops);

-- Índice para a chave estrangeira
CREATE INDEX idx_orders_o_custkey ON orders (o_custkey);

select
	c_count,
	count(*) as custdist
from
	(
		select
			c_custkey,
			count(o_orderkey) as c_count
		from
			customer left outer join orders on
				c_custkey = o_custkey
				and o_comment not like '%special%requests%'
		group by
			c_custkey
	) as c_orders
group by
	c_count
order by
	custdist desc,
	c_count desc;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 21.109,93 ms   | 18.625,10 ms   |                     |
| **Custo Inicial Estimado** | 1.558.139,44   | 1.546.201,08   |                     |
| **Custo Total Estimado**   | 1.558.139,94   | 1.546.201,58   |                     |
| **Linhas**                 | 200            | 200            |                     |
| **Memória: Hit**           | 17             | 45             |                     |
| **Memória: Read**          | 297.127        | 265.300        |                     |
| **Memória: Dirtied**       | -              | -              |                     |
| **Memória: Written**       | 140.929        | 141.245        |                     |
| **Temp Read**              | 101.072        | 101.419        |                     |
| **Temp Written**           | -              | -              |                     |

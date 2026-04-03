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
| **Tempo de Execução**      | 46.520,75 ms   |                |                     |
| **Custo Inicial Estimado** | 3.133.582,20   |                |                     |
| **Custo Total Estimado**   | 3.133.582,70   |                |                     |
| **Linhas**                 | 200            |                |                     |
| **Memória: Hit**           | 3              |                |                     |
| **Memória: Read**          | 594.275        |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 216.736        |                |                     |
| **Temp Written**           | 325.203        |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

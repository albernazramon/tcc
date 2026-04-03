# Comparação de Resultados: Cenário 3

## Queries Analisadas

### Pré-Otimização:

**Problema:** A lentidão deve-se principalmente à ausência de índices nas colunas de filtro (`c_mktsegment`, `o_orderdate`, `l_shipdate`) e de chaves estrangeiras, forçando varreduras sequenciais (Seq Scans) e junções ineficientes em tabelas grandes. Além disso, a agregação seguida de uma ordenação explícita por um valor calculado (`revenue DESC`) em um grande volume de dados intermediários é um gargalo significativo, especialmente antes de aplicar o `LIMIT 10`.

```sql
-- using default substitutions


select
	l_orderkey,
	sum(l_extendedprice * (1 - l_discount)) as revenue,
	o_orderdate,
	o_shippriority
from
	customer,
	orders,
	lineitem
where
	c_mktsegment = 'BUILDING'
	and c_custkey = o_custkey
	and l_orderkey = o_orderkey
	and o_orderdate < date '1995-03-15'
	and l_shipdate > date '1995-03-15'
group by
	l_orderkey,
	o_orderdate,
	o_shippriority
order by
	revenue desc,
	o_orderdate
limit 10;
```

### Pós-Otimização:

**Alterações:** Foram criados índices estratégicos para acelerar filtros e junções. O destaque é o **índice de cobertura** na tabela `lineitem` (`l_orderkey`, `l_shipdate`) incluindo as colunas de preço e desconto, o que permite um **Index-Only Scan**, eliminando acessos ao heap da tabela e reduzindo drasticamente o I/O. Índices nas colunas de filtro das tabelas `customer` e `orders` permitem que o otimizador utilize **Index Nested Loop Joins**, processando um volume muito menor de dados para a agregação e ordenação final.

```sql
-- Índices para a tabela customer
CREATE INDEX idx_customer_mktsegment ON public.customer (c_mktsegment);
CREATE INDEX idx_customer_custkey ON public.customer (c_custkey);

-- Índices para a tabela orders
CREATE INDEX idx_orders_custkey ON public.orders (o_custkey);
CREATE INDEX idx_orders_orderkey ON public.orders (o_orderkey);
CREATE INDEX idx_orders_orderdate_shippriority ON public.orders (o_orderdate, o_shippriority);

-- Índice de cobertura para a tabela lineitem
CREATE INDEX idx_lineitem_orderkey_shipdate_include_price_discount
ON public.lineitem (l_orderkey, l_shipdate)
INCLUDE (l_extendedprice, l_discount);

select
	l_orderkey,
	sum(l_extendedprice * (1 - l_discount)) as revenue,
	o_orderdate,
	o_shippriority
from
	customer,
	orders,
	lineitem
where
	c_mktsegment = 'BUILDING'
	and c_custkey = o_custkey
	and l_orderkey = o_orderkey
	and o_orderdate < date '1995-03-15'
	and l_shipdate > date '1995-03-15'
group by
	l_orderkey,
	o_orderdate,
	o_shippriority
order by
	revenue desc,
	o_orderdate
limit 10;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 93.252,54 ms   |                |                     |
| **Custo Inicial Estimado** | 5.559.505,19   |                |                     |
| **Custo Total Estimado**   | 5.559.505,22   |                |                     |
| **Linhas**                 | 10             |                |                     |
| **Memória: Hit**           | 33             |                |                     |
| **Memória: Read**          | 2.844.907      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | 375.282        |                |                     |
| **Temp Written**           | 375.577        |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

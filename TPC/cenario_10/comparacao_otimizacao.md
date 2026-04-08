# Comparação de Resultados: Cenário 10

## Queries Analisadas

### Pré-Otimização:

**Problema:** A consulta sofre com a falta de índices em colunas de filtro (`o_orderdate`, `l_returnflag`) e de chaves estrangeiras, forçando varreduras sequenciais (`Seq Scan`) e junções ineficientes (prováveis `Nested Loop` ou `Hash Join` lentos). O agrupamento por múltiplas colunas e a ordenação de um valor agregado (`revenue DESC`) também sobrecarregam a CPU e memória.

```sql
-- using default substitutions


select
	c_custkey,
	c_name,
	sum(l_extendedprice * (1 - l_discount)) as revenue,
	c_acctbal,
	n_name,
	c_address,
	c_phone,
	c_comment
from
	customer,
	orders,
	lineitem,
	nation
where
	c_custkey = o_custkey
	and l_orderkey = o_orderkey
	and o_orderdate >= date '1993-10-01'
	and o_orderdate < date '1993-10-01' + interval '3 months'
	and l_returnflag = 'R'
	and c_nationkey = n_nationkey
group by
	c_custkey,
	c_name,
	c_acctbal,
	c_phone,
	n_name,
	c_address,
	c_comment
order by
	revenue desc
limit 20;
```

### Pós-Otimização:

**Alterações:** A consulta foi reescrita utilizando **INNER JOIN explícito** e aliases para maior clareza. A otimização foca na criação de índices compostos estratégicos: um em `orders` para acelerar o filtro de data e a junção, e outro em `lineitem` que, além de filtrar por `l_returnflag`, inclui as colunas de preço e desconto para permitir um **Index-Only Scan**, reduzindo drasticamente o I/O de disco. A ordenação final com `LIMIT 20` também é beneficiada pela redução do volume de dados processados.

```sql
-- Índice para a tabela orders: filtra por data e otimiza junções
CREATE INDEX IF NOT EXISTS idx_orders_date_key_cust ON public.orders (o_orderdate, o_orderkey, o_custkey);

-- Índice para a tabela lineitem: filtra por returnflag, otimiza junção e cobre colunas para SUM
CREATE INDEX IF NOT EXISTS idx_lineitem_orderkey_returnflag_price_discount ON public.lineitem (l_orderkey, l_returnflag, l_extendedprice, l_discount);

-- Índice para a tabela customer: otimiza junções
CREATE INDEX IF NOT EXISTS idx_customer_custkey_nationkey ON public.customer (c_custkey, c_nationkey);

-- Índice para a tabela nation: otimiza junção
CREATE INDEX IF NOT EXISTS idx_nation_nationkey ON public.nation (n_nationkey);

select
	c.c_custkey,
	c.c_name,
	sum(l.l_extendedprice * (1 - l.l_discount)) as revenue,
	c.c_acctbal,
	n.n_name,
	c.c_address,
	c.c_phone,
	c.c_comment
from
	customer c
inner join orders o on c.c_custkey = o.o_custkey
inner join lineitem l on o.o_orderkey = l.l_orderkey
inner join nation n on c.c_nationkey = n.n_nationkey
where
	o.o_orderdate >= date '1993-10-01'
	and o.o_orderdate < date '1994-01-01'
	and l.l_returnflag = 'R'
group by
	c.c_custkey,
	c.c_name,
	c.c_acctbal,
	c.c_phone,
	n.n_name,
	c.c_address,
	c.c_comment
order by
	revenue desc
limit 20;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 38.409,64 ms   | 38.972,17 ms   |                     |
| **Custo Inicial Estimado** | 2.112.311,91   | 1.338.225,78   |                     |
| **Custo Total Estimado**   | 2.112.311,96   | 1.338.225,83   |                     |
| **Linhas**                 | 20             | 20             |                     |
| **Memória: Hit**           | 60             | 1.981.962      |                     |
| **Memória: Read**          | 1.422.256      | 587.355        |                     |
| **Memória: Dirtied**       | -              | -              |                     |
| **Memória: Written**       | 163.651        | 3              |                     |
| **Temp Read**              | 163.110        | 87.785         |                     |
| **Temp Written**           | -              | -              |                     |

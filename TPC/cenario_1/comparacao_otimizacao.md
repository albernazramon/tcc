# Comparação de Resultados: Cenário 1

## Queries Analisadas

### Pré-Otimização:

**Problema:** A consulta original apresenta gargalos devido à filtragem, agregação e ordenação em uma tabela grande sem índices adequados. A condição `WHERE l_shipdate` força uma varredura sequencial (Seq Scan), resultando em alto custo de I/O. Além disso, as cláusulas `GROUP BY` e `ORDER BY` exigem operações de HashAggregate ou Sort explícitas que são intensivas em CPU e memória, podendo até ocorrer "derramamento" para o disco.

```sql
select
	l_returnflag,
	l_linestatus,
	sum(l_quantity) as sum_qty,
	sum(l_extendedprice) as sum_base_price,
	sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
	sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
	avg(l_quantity) as avg_qty,
	avg(l_extendedprice) as avg_price,
	avg(l_discount) as avg_disc,
	count(*) as count_order
from
	lineitem
where
	l_shipdate <= date '1998-12-01' - interval '90 days'
group by
	l_returnflag,
	l_linestatus
order by
	l_returnflag,
	l_linestatus;
```

### Pós-Otimização:

**Alterações:** A otimização foca na criação de um índice B-tree composto (`l_shipdate`, `l_returnflag`, `l_linestatus`). Isso permite que o PostgreSQL utilize um Index Scan ou Bitmap Index Scan para o filtro de data, reduzindo drasticamente o I/O. O índice também fornece os dados pré-ordenados para as colunas de agrupamento, permitindo o uso de `GroupAggregate` (mais eficiente) e eliminando a necessidade de um `Sort` explícito para o `ORDER BY`.

```sql
CREATE INDEX idx_lineitem_shipdate_returnflag_linestatus
ON public.lineitem (l_shipdate, l_returnflag, l_linestatus);

select
	l_returnflag,
	l_linestatus,
	sum(l_quantity) as sum_qty,
	sum(l_extendedprice) as sum_base_price,
	sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
	sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
	avg(l_quantity) as avg_qty,
	avg(l_extendedprice) as avg_price,
	avg(l_discount) as avg_disc,
	count(*) as count_order
from
	lineitem
where
	l_shipdate <= date '1998-12-01' - interval '90 days'
group by
	l_returnflag,
	l_linestatus
order by
	l_returnflag,
	l_linestatus;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 56.042,08 ms   |                |                     |
| **Custo Inicial Estimado** | 4.598.926,95   |                |                     |
| **Custo Total Estimado**   | 4.598.929,20   |                |                     |
| **Linhas**                 | 6              |                |                     |
| **Memória: Hit**           | 14             |                |                     |
| **Memória: Read**          | 2.250.632      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | -              |                |                     |
| **Temp Written**           | -              |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

# Comparação de Resultados: Cenário 6

## Queries Analisadas

### Pré-Otimização:

**Problema:** A lentidão deve-se à ausência de índices na tabela `lineitem`, o que força o PostgreSQL a realizar um `Seq Scan` (varredura sequencial) completo para avaliar as condições de filtro (`l_shipdate`, `l_discount`, `l_quantity`). Isso resulta em um alto custo de I/O, lendo todas as páginas do disco independentemente da seletividade da consulta.

```sql
-- using default substitutions


select
	sum(l_extendedprice * l_discount) as revenue
from
	lineitem
where
	l_shipdate >= date '1994-01-01'
	and l_shipdate < date '1994-01-01' + interval '1 year'
	and l_discount between .06 - 0.01 and .06 + 0.01
	and l_quantity < 24;
```

### Pós-Otimização:

**Alterações:** A consulta SQL foi simplificada para maior clareza, mas a principal otimização é a criação de um **índice composto** (`l_shipdate`, `l_discount`, `l_quantity`). Esse índice permite que o planejador utilize estratégias de **Bitmap Index Scan** ou **Index Scan**, localizando rapidamente apenas as linhas que satisfazem os critérios e reduzindo drasticamente o número de blocos de disco lidos.

```sql
CREATE INDEX idx_lineitem_shipdate_discount_quantity
ON public.lineitem (l_shipdate, l_discount, l_quantity);

select
	sum(l_extendedprice * l_discount) as revenue
from
	lineitem
where
	l_shipdate >= '1994-01-01'
	and l_shipdate < '1995-01-01'
	and l_discount between 0.05 and 0.07
	and l_quantity < 24;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 57.891,58 ms   |                |                     |
| **Custo Inicial Estimado** | 3.381.417,81   |                |                     |
| **Custo Total Estimado**   | 3.381.417,82   |                |                     |
| **Linhas**                 | 1              |                |                     |
| **Memória: Hit**           | -              |                |                     |
| **Memória: Read**          | 2.250.632      |                |                     |
| **Memória: Dirtied**       | -              |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | -              |                |                     |
| **Temp Written**           | -              |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultados_consulta_original](.\resultados_consulta_original.csv)
- **Pós-Otimização:** [resultados_consulta_otimizada](.\resultados_consulta_otimizada.csv)

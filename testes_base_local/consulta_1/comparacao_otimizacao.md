# Comparação de Resultados: Consulta 1

## Queries Analisadas

### Pré-Otimização: Join sem índices e filtro ineficiente

**Problema:** Realiza um JOIN entre as duas maiores tabelas do banco sem garantia de índices nas chaves estrangeiras (se não criados) e usa um filtro `OR` que pode forçar um Sequential Scan.

```sql
SELECT
    o.o_orderkey,
    o.o_orderdate,
    l.l_extendedprice
FROM
    public.orders o
JOIN
    public.lineitem l ON o.o_orderkey = l.l_orderkey
WHERE
    o.o_orderstatus = 'F' OR l.l_quantity > 40;
```

### Pós-Otimização: Uso de UNION ALL e Criação de Índices

**Alterações:** O modelo alterou a consulta original, utilizando o UNION ALL e aplicando os filtros de forma separada.
Também indicou a criação dos seguintes índices:

```sql
CREATE INDEX IF NOT EXISTS ix_orders_orderkey ON public.orders (o_orderkey);
CREATE INDEX IF NOT EXISTS ix_lineitem_orderkey ON public.lineitem (l_orderkey);
CREATE INDEX IF NOT EXISTS ix_orders_orderstatus ON public.orders (o_orderstatus);
CREATE INDEX IF NOT EXISTS ix_lineitem_quantity ON public.lineitem (l_quantity);
```

```sql
SELECT
    o.o_orderkey,
    o.o_orderdate,
    l.l_extendedprice
FROM
    public.orders o
JOIN
    public.lineitem l ON o.o_orderkey = l.l_orderkey
WHERE
    o.o_orderstatus = 'F'

UNION ALL

SELECT
    o.o_orderkey,
    o.o_orderdate,
    l.l_extendedprice
FROM
    public.orders o
JOIN
    public.lineitem l ON o.o_orderkey = l.l_orderkey
WHERE
    l.l_quantity > 40
    AND o.o_orderstatus IS DISTINCT FROM 'F';
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto                               |
| :------------------------- | :------------- | :------------- | :------------------------------------------------ |
| **Tempo de Execução**      | 4992.034 ms    | 3276.480 ms    | Melhoria significativa                            |
| **Custo Inicial Estimado** | 279,133.51     | 17,057.70      | Redução massiva no custo de startup               |
| **Custo Total Estimado**   | 17,927,093.59  | 224,447,762.49 | Custo total subiu devido ao UNION ALL e seq scans |
| **Memória: Hit**           | 4              | 17,373         | Maior reaproveitamento de buffer                  |
| **Memória: Read**          | 110,384        | 238,995        | Mais leituras de disco no UNION ALL               |
| **Memória: Dirtied**       | 110,366        | N/A            | -                                                 |
| **Memória: Written**       | 92,452         | 7,357          | Redução drástica em escritas                      |
| **Temp Read**              | 33,731         | 12,033         | Redução de disco temporário                       |
| **Temp Written**           | 33,816         | 5,203          | Redução de disco temporário                       |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultado_pre_otimizacao](.\resultado_pre_otimizacao.csv)
- **Pós-Otimização:** [resultado_pos_otimizacao](.\resultado_pos_otimizacao.csv)
  _(Os resultados apresentam a mesma quantidade de linhas, porém os dados não estão ordenados da mesma forma que no resultado da consulta original, devido à mudança de plano de execução com o `UNION ALL`.)_

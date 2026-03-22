# Comparação de Resultados: Consulta 1

## Queries Analisadas

### Pré-Otimização: Join sem índices e filtro ineficiente

**Problema:** Realiza um JOIN entre as duas maiores tabelas do banco sem garantia de índices nas chaves estrangeiras (se não criados) e usa um filtro `OR` que pode forçar um Sequential Scan.

```sql
SELECT DISTINCT
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
CREATE INDEX idx_orders_orderstatus ON public.orders (o_orderstatus);
CREATE INDEX idx_lineitem_quantity ON public.lineitem (l_quantity);
CREATE INDEX idx_orders_orderkey ON public.orders (o_orderkey);
CREATE INDEX idx_lineitem_orderkey ON public.lineitem (l_orderkey);
```

```sql
SELECT DISTINCT
    o_orderkey,
    o_orderdate,
    l_extendedprice
FROM (
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
) AS combined_results;
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto                              |
| :------------------------- | :------------- | :------------- | :----------------------------------------------- |
| **Tempo de Execução**      | 4992.034 ms    | 2310.754       | Melhoria significativa                           |
| **Custo Inicial Estimado** | 279,133.51     | 562,542.48     | Aumento no custo de startup                      |
| **Custo Total Estimado**   | 17,927,093.59  | 678.721.81     | Redução massiva no custo total                   |
| **Linhas**                 | 297.023.601    | 345.067        | Redução drástica no número de linhas percorridas |
| **Memória: Hit**           | 4              | 2.479.540      | Maior reaproveitamento de buffer                 |
| **Memória: Read**          | 110,384        | 224.689        | Mais leituras de disco pós-otimização            |
| **Memória: Dirtied**       | 110,366        | N/A            | -                                                |
| **Memória: Written**       | 92,452         | 14.081         | Redução drástica em escritas                     |
| **Temp Read**              | 33,731         | 17.215         | Redução de disco temporário                      |
| **Temp Written**           | 33,816         | 17.268         | Redução de disco temporário                      |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultado_pre_otimizacao](.\resultado_pre_otimizacao.csv)
- **Pós-Otimização:** [resultado_pos_otimizacao](.\resultado_pos_otimizacao.csv)
  _(Os resultados pré-otimização apresentam 5 linhas a menos, e isso se deve ao fato do uso do DISTINCT que está eliminando registros duplicados. Ao testar a consulta original utilizando o DISTINCT, foram identificadas que o resultado fica igual ao resultado pós-otimização. ALém disso, os dados não estão ordenados da mesma forma que no resultado da consulta original, devido à mudança de plano de execução com o `UNION ALL`.)_

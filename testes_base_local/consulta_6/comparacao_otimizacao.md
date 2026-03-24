# Comparação de Resultados: Consulta 6

## Queries Analisadas

### Pré-Otimização: UNION desnecessário em vez de UNION ALL

**Problema:** O `UNION` realiza uma operação de `DISTINCT` pesada para remover duplicatas que, neste contexto de negócio (pedidos urgentes vs alta prioridade), podem ser aceitáveis ou tratadas de outra forma, economizando processamento.

```sql
SELECT o_orderkey, o_orderpriority FROM public.orders WHERE o_orderpriority = '1-URGENT'
UNION
SELECT o_orderkey, o_orderpriority FROM public.orders WHERE o_orderstatus = 'O';
```

### Pós-Otimização: Alteração de UNION para WHERE e criação de índices

**Alterações:** A consulta foi alterada sintaticamente para utilizar um filtro WHERE com as duas clausulas no lugar do UNION.

```sql
SELECT o_orderkey, o_orderpriority
FROM public.orders
WHERE o_orderpriority = '1-URGENT' OR o_orderstatus = 'O';
```

O modelo também sugeriu a criação dos seguintes índices:

```sql
CREATE INDEX idx_orders_orderpriority ON public.orders (o_orderpriority);
CREATE INDEX idx_orders_orderstatus ON public.orders (o_orderstatus);
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto                |
| :------------------------- | :------------- | :------------- | :--------------------------------- |
| **Tempo de Execução**      | 902.407 ms     | 232.343 ms     | Redução significativa              |
| **Custo Inicial Estimado** | 56545.38       | 176.84         | Redução drástica                   |
| **Custo Total Estimado**   | 56565.03       | 23708.26       | Redução                            |
| **Linhas**                 | 2620           | 14962          | Mais linhas envolvidas na consulta |
| **Memória: Hit**           | 26019          | 188            | Menor reaproveitamento ded buffer  |
| **Memória: Read**          | 26376          | 26889          | Leve aumento na leitura de memória |
| **Memória: Dirtied**       | 26200          | -              | Sem memória suja                   |
| **Memória: Written**       | 10021          | 15189          | Aumento na memória escrita         |
| **Temp Read**              | 2941           | -              | Sem uso de memória temporária      |
| **Temp Written**           | 2955           | -              | Sem uso de memória temporária      |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultado_pre_otimizacao](.\resultado_pre_otimizacao.csv)
- **Pós-Otimização:** [resultado_pos_otimizacao](.\resultado_pos_otimizacao.csv)
  \_(Os resultados apresentam a mesma quantidade de linhas, porém o conteúdo está ordenado de forma diferente, o que se deve ao fato do novo plano de execução com indexação.)

# Consultas

## Query 5: Filtro LIKE com wildcard no início

**Problema:** O uso de `%` no início da string de busca impossibilita o uso de índices padrão, forçando a leitura de toda a tabela `supplier`.

```sql
SELECT
    s_name,
    s_address
FROM
    public.supplier
WHERE
    s_comment LIKE '%special packages%';
```

## Query 6: UNION desnecessário em vez de UNION ALL

**Problema:** O `UNION` realiza uma operação de `DISTINCT` pesada para remover duplicatas que, neste contexto de negócio (pedidos urgentes vs alta prioridade), podem ser aceitáveis ou tratadas de outra forma, economizando processamento.

```sql
SELECT o_orderkey, o_orderpriority FROM public.orders WHERE o_orderpriority = '1-URGENT'
UNION
SELECT o_orderkey, o_orderpriority FROM public.orders WHERE o_orderstatus = 'O';
```

# Consultas

Este documento contém 6 consultas SQL foram geradas com o modelo gemini-3-flash-preview, com o intuito de ter consultas com problemas de performance.

## Query 2: Uso de funções em colunas no WHERE (SARGability)

**Problema:** O uso de `UPPER()` na coluna `c_name` impede o uso de índices B-tree padrão, resultando em um Full Table Scan na tabela `customer`.

```sql
SELECT
    c_name,
    c_acctbal
FROM
    public.customer
WHERE
    UPPER(c_name) LIKE 'CUSTOMER#000000001%';
```

## Query 3: Subconsulta correlacionada pesada

**Problema:** A subconsulta é executada para cada linha da tabela `part`, o que é extremamente ineficiente para grandes volumes. Deveria ser um JOIN com agregação.

```sql
SELECT
    p.p_name,
    (SELECT SUM(l.l_quantity)
     FROM public.lineitem l
     WHERE l.l_partkey = p.p_partkey) as total_qty
FROM
    public.part p
WHERE
    p.p_size > 10;
```

## Query 4: Ordenação global de grande volume sem índice

**Problema:** Ordenar 4.4 milhões de registros por uma coluna não indexada causará um Sort em disco extremamente lento.

```sql
SELECT
    l_orderkey,
    l_partkey,
    l_shipdate
FROM
    public.lineitem
ORDER BY
    l_shipdate DESC
LIMIT 100;
```

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

# Banco de dados original

## Quantidade de registros

| Tabela   | Registros |
| -------- | --------- |
| customer | 150.000   |
| lineitem | 4.423.659 |
| nation   | 25        |
| orders   | 1.500.000 |
| part     | 200.000   |
| partsupp | 800.000   |
| region   | 5         |
| supplier | 10.000    |

## Memória ocupada por tabela

Consulta utilizada: `SELECT pg_size_pretty(pg_total_relation_size('<schema>.<table>'));`

| Tabela    | Memória     |
|-----------|-------------|
| customer  | 28 MB       |
| lineitem  | 658 MB      |
| nation    | 8192 bytes  |
| orders    | 205 MB      |
| part      | 29 MB       |
| partsupp  | 135 MB      |
| region    | 8192 bytes  |
| supplier  | 1672 kB     |

## ESQUEMAS

```sql
CREATE TABLE IF NOT EXISTS public.customer
(
    c_custkey integer,
    c_mktsegment character varying(50) COLLATE pg_catalog."default",
    c_nationkey integer,
    c_name character varying(50) COLLATE pg_catalog."default",
    c_address character varying(50) COLLATE pg_catalog."default",
    c_phone character varying(50) COLLATE pg_catalog."default",
    c_acctbal real,
    c_comment character varying(128) COLLATE pg_catalog."default"
)
```

```sql
CREATE TABLE IF NOT EXISTS public.lineitem
(
    l_shipdate character varying(50) COLLATE pg_catalog."default",
    l_orderkey integer,
    l_discount real,
    l_extendedprice real,
    l_suppkey integer,
    l_quantity integer,
    l_returnflag character varying(50) COLLATE pg_catalog."default",
    l_partkey integer,
    l_linestatus character varying(50) COLLATE pg_catalog."default",
    l_tax real,
    l_commitdate character varying(50) COLLATE pg_catalog."default",
    l_receiptdate character varying(50) COLLATE pg_catalog."default",
    l_shipmode character varying(50) COLLATE pg_catalog."default",
    l_linenumber integer,
    l_shipinstruct character varying(50) COLLATE pg_catalog."default",
    l_comment character varying(50) COLLATE pg_catalog."default"
)
```

```sql
CREATE TABLE IF NOT EXISTS public.nation
(
    n_nationkey integer,
    n_name character varying(50) COLLATE pg_catalog."default",
    n_regionkey integer,
    n_comment character varying(128) COLLATE pg_catalog."default"
)
```

```sql
CREATE TABLE IF NOT EXISTS public.orders
(
    o_orderdate character varying(50) COLLATE pg_catalog."default",
    o_orderkey integer,
    o_custkey integer,
    o_orderpriority character varying(50) COLLATE pg_catalog."default",
    o_shippriority integer,
    o_clerk character varying(50) COLLATE pg_catalog."default",
    o_orderstatus character varying(50) COLLATE pg_catalog."default",
    o_totalprice real,
    o_comment character varying(128) COLLATE pg_catalog."default"
)
```

```sql
CREATE TABLE IF NOT EXISTS public.part
(
    p_partkey integer,
    p_type character varying(50) COLLATE pg_catalog."default",
    p_size integer,
    p_brand character varying(50) COLLATE pg_catalog."default",
    p_name character varying(50) COLLATE pg_catalog."default",
    p_container character varying(50) COLLATE pg_catalog."default",
    p_mfgr character varying(50) COLLATE pg_catalog."default",
    p_retailprice real,
    p_comment character varying(50) COLLATE pg_catalog."default"
)
```

```sql
CREATE TABLE IF NOT EXISTS public.partsupp
(
    ps_partkey integer,
    ps_suppkey integer,
    ps_supplycost real,
    ps_availqty integer,
    ps_comment character varying(256) COLLATE pg_catalog."default"
)
```

```sql
CREATE TABLE IF NOT EXISTS public.region
(
    r_regionkey integer,
    r_name character varying(50) COLLATE pg_catalog."default",
    r_comment character varying(128) COLLATE pg_catalog."default"
)
```

```sql
CREATE TABLE IF NOT EXISTS public.supplier
(
    s_suppkey integer,
    s_nationkey integer,
    s_comment character varying(128) COLLATE pg_catalog."default",
    s_name character varying(50) COLLATE pg_catalog."default",
    s_address character varying(50) COLLATE pg_catalog."default",
    s_phone character varying(50) COLLATE pg_catalog."default",
    s_acctbal real
)
```

# Query

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

# Schemas

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

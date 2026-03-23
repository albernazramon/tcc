# Query

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

# Schemas

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

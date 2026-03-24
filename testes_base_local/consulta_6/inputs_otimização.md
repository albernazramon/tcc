# Query

```sql
SELECT o_orderkey, o_orderpriority FROM public.orders WHERE o_orderpriority = '1-URGENT'
UNION
SELECT o_orderkey, o_orderpriority FROM public.orders WHERE o_orderstatus = 'O';
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

```

# Query

```sql
SELECT
    c_name,
    c_acctbal
FROM
    public.customer
WHERE
    UPPER(c_name) LIKE 'CUSTOMER#000000001%';
```

# Schemas

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

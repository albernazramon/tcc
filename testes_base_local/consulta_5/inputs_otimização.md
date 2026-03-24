# Query

```sql
SELECT
    s_name,
    s_address
FROM
    public.supplier
WHERE
    s_comment LIKE '%special packages%';
```

# Schemas

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

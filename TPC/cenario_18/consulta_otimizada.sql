WITH OrderQuantities AS (
    SELECT
        l_orderkey,
        SUM(l_quantity) AS total_quantity_for_order
    FROM
        lineitem
    GROUP BY
        l_orderkey
    HAVING
        SUM(l_quantity) > 300
)
SELECT
    c.c_name,
    c.c_custkey,
    o.o_orderkey,
    o.o_orderdate,
    o.o_totalprice,
    oq.total_quantity_for_order
FROM
    customer c
JOIN
    orders o ON c.c_custkey = o.o_custkey
JOIN
    OrderQuantities oq ON o.o_orderkey = oq.l_orderkey
ORDER BY
    o.o_totalprice DESC,
    o.o_orderdate
LIMIT 100;
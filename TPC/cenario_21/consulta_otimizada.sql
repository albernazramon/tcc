WITH orders_with_multiple_suppliers AS (
    SELECT
        l_orderkey
    FROM
        lineitem
    GROUP BY
        l_orderkey
    HAVING
        COUNT(DISTINCT l_suppkey) > 1
),
orders_suppliers_with_late_others AS (
    SELECT DISTINCT
        l1.l_orderkey,
        l1.l_suppkey
    FROM
        lineitem l1
    JOIN
        lineitem l3 ON l1.l_orderkey = l3.l_orderkey
    WHERE
        l1.l_suppkey <> l3.l_suppkey
        AND l3.l_receiptdate > l3.l_commitdate
)
SELECT
    s.s_name,
    COUNT(*) AS numwait
FROM
    nation n
JOIN
    supplier s ON s.s_nationkey = n.n_nationkey
JOIN
    lineitem l1 ON s.s_suppkey = l1.l_suppkey
JOIN
    orders o ON l1.l_orderkey = o.o_orderkey
LEFT JOIN
    orders_suppliers_with_late_others oslo ON l1.l_orderkey = oslo.l_orderkey AND l1.l_suppkey = oslo.l_suppkey
WHERE
    n.n_name = 'SAUDI ARABIA'
    AND o.o_orderstatus = 'F'
    AND l1.l_receiptdate > l1.l_commitdate
    AND l1.l_orderkey IN (SELECT l_orderkey FROM orders_with_multiple_suppliers)
    AND oslo.l_orderkey IS NULL
GROUP BY
    s.s_name
ORDER BY
    numwait DESC,
    s_name
LIMIT 100;
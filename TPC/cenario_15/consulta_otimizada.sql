WITH supplier_revenue AS (
    SELECT
        l_suppkey,
        sum(l_extendedprice * (1 - l_discount)) AS total_revenue
    FROM
        lineitem
    WHERE
        l_shipdate >= date '1996-01-01'
        AND l_shipdate < date '1996-04-01'
    GROUP BY
        l_suppkey
)
SELECT
    s.s_suppkey,
    s.s_name,
    s.s_address,
    s.s_phone,
    sr.total_revenue
FROM
    supplier s
JOIN
    supplier_revenue sr ON s.s_suppkey = sr.l_suppkey
WHERE
    sr.total_revenue = (SELECT max(total_revenue) FROM supplier_revenue)
ORDER BY
    s.s_suppkey;
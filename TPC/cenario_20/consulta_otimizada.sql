SELECT
    s.s_name,
    s.s_address
FROM
    supplier s
JOIN
    nation n ON s.s_nationkey = n.n_nationkey
JOIN
    partsupp ps ON s.s_suppkey = ps.ps_suppkey
JOIN
    part p ON ps.ps_partkey = p.p_partkey
JOIN (
    SELECT
        l_partkey,
        l_suppkey,
        0.5 * SUM(l_quantity) AS half_sum_quantity
    FROM
        lineitem
    WHERE
        l_shipdate >= DATE '1994-01-01'
        AND l_shipdate < DATE '1995-01-01'
    GROUP BY
        l_partkey,
        l_suppkey
) AS li_agg ON ps.ps_partkey = li_agg.l_partkey AND ps.ps_suppkey = li_agg.l_suppkey
WHERE
    n.n_name = 'CANADA'
    AND p.p_name LIKE 'forest%'
    AND ps.ps_availqty > li_agg.half_sum_quantity
ORDER BY
    s.s_name;
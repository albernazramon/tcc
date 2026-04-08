SELECT
    n.n_name AS nation,
    EXTRACT(YEAR FROM o.o_orderdate) AS o_year,
    SUM(l.l_extendedprice * (1 - l.l_discount) - ps.ps_supplycost * l.l_quantity) AS sum_profit
FROM
    part AS p
JOIN
    lineitem AS l ON p.p_partkey = l.l_partkey
JOIN
    partsupp AS ps ON l.l_partkey = ps.ps_partkey AND l.l_suppkey = ps.ps_suppkey
JOIN
    supplier AS s ON l.l_suppkey = s.s_suppkey
JOIN
    orders AS o ON l.l_orderkey = o.o_orderkey
JOIN
    nation AS n ON s.s_nationkey = n.n_nationkey
WHERE
    p.p_name LIKE '%green%'
GROUP BY
    n.n_name,
    EXTRACT(YEAR FROM o.o_orderdate)
ORDER BY
    n.n_name,
    EXTRACT(YEAR FROM o.o_orderdate) DESC;
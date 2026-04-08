SELECT
    n.n_name,
    SUM(l.l_extendedprice * (1 - l.l_discount)) AS revenue
FROM
    region AS r
JOIN
    nation AS n ON n.n_regionkey = r.r_regionkey
JOIN
    supplier AS s ON s.s_nationkey = n.n_nationkey
JOIN
    customer AS c ON c.c_nationkey = s.s_nationkey
JOIN
    orders AS o ON o.o_custkey = c.c_custkey
JOIN
    lineitem AS l ON l.l_orderkey = o.o_orderkey AND l.l_suppkey = s.s_suppkey
WHERE
    r.r_name = 'ASIA'
    AND o.o_orderdate >= DATE '1994-01-01'
    AND o.o_orderdate < DATE '1994-01-01' + INTERVAL '1 year'
GROUP BY
    n.n_name
ORDER BY
    revenue DESC;
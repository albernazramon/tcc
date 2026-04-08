SELECT
    EXTRACT(YEAR FROM o.o_orderdate) AS o_year,
    SUM(CASE
        WHEN n2.n_name = 'BRAZIL' THEN l.l_extendedprice * (1 - l.l_discount)
        ELSE 0
    END) / SUM(l.l_extendedprice * (1 - l.l_discount)) AS mkt_share
FROM
    part p
JOIN
    lineitem l ON p.p_partkey = l.l_partkey
JOIN
    supplier s ON s.s_suppkey = l.l_suppkey
JOIN
    orders o ON l.l_orderkey = o.o_orderkey
JOIN
    customer c ON o.o_custkey = c.c_custkey
JOIN
    nation n1 ON c.c_nationkey = n1.n_nationkey
JOIN
    region r ON n1.n_regionkey = r.r_regionkey
JOIN
    nation n2 ON s.s_nationkey = n2.n_nationkey
WHERE
    r.r_name = 'AMERICA'
    AND o.o_orderdate BETWEEN DATE '1995-01-01' AND DATE '1996-12-31'
    AND p.p_type = 'ECONOMY ANODIZED STEEL'
GROUP BY
    o_year
ORDER BY
    o_year;
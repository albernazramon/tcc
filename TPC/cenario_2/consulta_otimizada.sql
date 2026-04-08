WITH MinSupplyCost AS (
    SELECT
        ps.ps_partkey,
        MIN(ps.ps_supplycost) AS min_ps_supplycost_europe
    FROM
        public.partsupp ps
    JOIN
        public.supplier s ON ps.ps_suppkey = s.s_suppkey
    JOIN
        public.nation n ON s.s_nationkey = n.n_nationkey
    JOIN
        public.region r ON n.n_regionkey = r.r_regionkey
    WHERE
        r.r_name = 'EUROPE'
    GROUP BY
        ps.ps_partkey
)
SELECT
    s.s_acctbal,
    s.s_name,
    n.n_name,
    p.p_partkey,
    p.p_mfgr,
    s.s_address,
    s.s_phone,
    s.s_comment
FROM
    public.part p
JOIN
    public.partsupp ps ON p.p_partkey = ps.ps_partkey
JOIN
    public.supplier s ON s.s_suppkey = ps.ps_suppkey
JOIN
    public.nation n ON s.s_nationkey = n.n_nationkey
JOIN
    public.region r ON n.n_regionkey = r.r_regionkey
JOIN
    MinSupplyCost msc ON ps.ps_partkey = msc.ps_partkey AND ps.ps_supplycost = msc.min_ps_supplycost_europe
WHERE
    p.p_size = 15
    AND p.p_type LIKE '%BRASS'
    AND r.r_name = 'EUROPE'
ORDER BY
    s.s_acctbal DESC,
    n.n_name ASC,
    s.s_name ASC,
    p.p_partkey ASC
LIMIT 100;
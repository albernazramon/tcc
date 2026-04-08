WITH FilteredCustomers AS (
    SELECT
        c.c_custkey,
        substring(c.c_phone FROM 1 FOR 2) AS cntrycode,
        c.c_acctbal
    FROM
        customer c
    WHERE
        substring(c.c_phone FROM 1 FOR 2) IN ('13', '31', '23', '29', '30', '18', '17')
        AND c.c_acctbal > 0.00
),
AvgFilteredAcctBal AS (
    SELECT AVG(fc.c_acctbal) AS avg_bal
    FROM FilteredCustomers fc
)
SELECT
    fc.cntrycode,
    COUNT(fc.c_custkey) AS numcust,
    SUM(fc.c_acctbal) AS totacctbal
FROM
    FilteredCustomers fc
CROSS JOIN
    AvgFilteredAcctBal afab
LEFT JOIN
    orders o ON fc.c_custkey = o.o_custkey
WHERE
    fc.c_acctbal > afab.avg_bal
    AND o.o_orderkey IS NULL
GROUP BY
    fc.cntrycode
ORDER BY
    fc.cntrycode;
WITH PartAvgQuantity AS (
    SELECT
        l_partkey,
        0.2 * AVG(l_quantity) AS avg_qty_threshold
    FROM
        lineitem
    GROUP BY
        l_partkey
)
SELECT
    SUM(li.l_extendedprice) / 7.0 AS avg_yearly
FROM
    lineitem li
JOIN
    part p ON p.p_partkey = li.l_partkey
JOIN
    PartAvgQuantity paq ON li.l_partkey = paq.l_partkey
WHERE
    p.p_brand = 'Brand#23'
    AND p.p_container = 'MED BOX'
    AND li.l_quantity < paq.avg_qty_threshold;
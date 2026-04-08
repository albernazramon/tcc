SELECT
    ps_partkey,
    value
FROM (
    SELECT
        ps_partkey,
        sum(ps_supplycost * ps_availqty) AS value,
        sum(sum(ps_supplycost * ps_availqty)) OVER () AS total_germany_value
    FROM
        partsupp
    JOIN
        supplier ON ps_suppkey = s_suppkey
    JOIN
        nation ON s_nationkey = n_nationkey
    WHERE
        n_name = 'GERMANY'
    GROUP BY
        ps_partkey
) AS grouped_values_with_total
WHERE
    value > total_germany_value * 0.0001000000
ORDER BY
    value DESC;
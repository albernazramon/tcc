SELECT
    o.o_orderpriority,
    COUNT(o.o_orderkey) AS order_count
FROM
    orders o
JOIN (
    SELECT DISTINCT l_orderkey
    FROM lineitem
    WHERE l_commitdate < l_receiptdate
) AS filtered_lineitems ON o.o_orderkey = filtered_lineitems.l_orderkey
WHERE
    o.o_orderdate >= DATE '1993-07-01'
    AND o.o_orderdate < DATE '1993-07-01' + INTERVAL '3 months'
GROUP BY
    o.o_orderpriority
ORDER BY
    o.o_orderpriority;
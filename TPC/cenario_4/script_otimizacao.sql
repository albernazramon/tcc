-- Índice para a tabela lineitem
CREATE INDEX IF NOT EXISTS idx_lineitem_commit_receipt_orderkey ON lineitem (l_commitdate, l_receiptdate, l_orderkey);

-- Índice para a tabela orders
CREATE INDEX IF NOT EXISTS idx_orders_date_priority_key ON orders (o_orderdate, o_orderpriority, o_orderkey);
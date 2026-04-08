-- Índices Recomendados
CREATE INDEX IF NOT EXISTS idx_nation_name ON nation (n_name);

CREATE INDEX IF NOT EXISTS idx_supplier_nationkey ON supplier (s_nationkey);

CREATE INDEX IF NOT EXISTS idx_orders_orderstatus ON orders (o_orderstatus);

CREATE INDEX IF NOT EXISTS idx_orders_orderkey ON orders (o_orderkey);

CREATE INDEX IF NOT EXISTS idx_lineitem_composite ON lineitem (l_orderkey, l_suppkey, l_receiptdate, l_commitdate);
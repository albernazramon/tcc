-- Índice para a CTE de agregação
CREATE INDEX IF NOT EXISTS idx_lineitem_orderkey_quantity ON public.lineitem (l_orderkey, l_quantity);

-- Índice composto para ORDER BY, LIMIT e junções
CREATE INDEX IF NOT EXISTS idx_orders_totalprice_date_custkey_orderkey ON public.orders (o_totalprice DESC, o_orderdate, o_custkey, o_orderkey);

-- Índices para chaves de junção
CREATE INDEX IF NOT EXISTS idx_orders_custkey ON public.orders (o_custkey);

CREATE INDEX IF NOT EXISTS idx_customer_custkey ON public.customer (c_custkey);
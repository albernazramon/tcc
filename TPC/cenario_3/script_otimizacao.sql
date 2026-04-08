-- Índices para a tabela customer
CREATE INDEX IF NOT EXISTS idx_customer_mktsegment ON public.customer (c_mktsegment);

CREATE INDEX IF NOT EXISTS idx_customer_custkey ON public.customer (c_custkey);

-- Índices para a tabela orders
CREATE INDEX IF NOT EXISTS idx_orders_custkey ON public.orders (o_custkey);

CREATE INDEX IF NOT EXISTS idx_orders_orderkey ON public.orders (o_orderkey);

CREATE INDEX IF NOT EXISTS idx_orders_orderdate_shippriority ON public.orders (o_orderdate, o_shippriority);

-- Índice de cobertura para a tabela lineitem
CREATE INDEX IF NOT EXISTS idx_lineitem_orderkey_shipdate_include_price_discount
ON public.lineitem (l_orderkey, l_shipdate)
INCLUDE (l_extendedprice, l_discount);
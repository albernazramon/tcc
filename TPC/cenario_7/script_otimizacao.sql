-- Índices em Chaves Estrangeiras
CREATE INDEX IF NOT EXISTS idx_lineitem_suppkey ON public.lineitem (l_suppkey);

CREATE INDEX IF NOT EXISTS idx_orders_custkey ON public.orders (o_custkey);

CREATE INDEX IF NOT EXISTS idx_supplier_nationkey ON public.supplier (s_nationkey);

CREATE INDEX IF NOT EXISTS idx_customer_nationkey ON public.customer (c_nationkey);

-- Índices para Filtros e Ordenação
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate ON public.lineitem (l_shipdate);

CREATE INDEX IF NOT EXISTS idx_nation_name ON public.nation (n_name);
-- Filtros
CREATE INDEX IF NOT EXISTS idx_region_r_name ON public.region (r_name);

CREATE INDEX IF NOT EXISTS idx_orders_o_orderdate ON public.orders (o_orderdate);

-- Junções (Nation, Supplier, Customer)
CREATE INDEX IF NOT EXISTS idx_nation_n_regionkey ON public.nation (n_regionkey);

CREATE INDEX IF NOT EXISTS idx_supplier_s_nationkey ON public.supplier (s_nationkey);

CREATE INDEX IF NOT EXISTS idx_customer_c_nationkey ON public.customer (c_nationkey);

-- Junções (Orders, Lineitem)
CREATE INDEX IF NOT EXISTS idx_orders_o_custkey ON public.orders (o_custkey);

CREATE INDEX IF NOT EXISTS idx_lineitem_l_orderkey ON public.lineitem (l_orderkey);

CREATE INDEX IF NOT EXISTS idx_lineitem_l_suppkey ON public.lineitem (l_suppkey);
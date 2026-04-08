-- Índices Recomendados
CREATE INDEX IF NOT EXISTS idx_part_p_name ON public.part (p_name);

CREATE INDEX IF NOT EXISTS idx_nation_n_name ON public.nation (n_name);

CREATE INDEX IF NOT EXISTS idx_supplier_s_nationkey ON public.supplier (s_nationkey);

CREATE INDEX IF NOT EXISTS idx_supplier_s_suppkey ON public.supplier (s_suppkey);

CREATE INDEX IF NOT EXISTS idx_partsupp_ps_suppkey_ps_partkey ON public.partsupp (ps_suppkey, ps_partkey);

CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate_partkey_suppkey ON public.lineitem (l_shipdate, l_partkey, l_suppkey);
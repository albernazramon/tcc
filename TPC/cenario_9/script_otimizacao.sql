-- Habilita a extensão pg_trgm para buscas de texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_part_p_name_trgm ON public.part USING GIN (p_name gin_trgm_ops);

-- Índices para otimizar as junções (chaves estrangeiras)
CREATE INDEX IF NOT EXISTS idx_lineitem_partkey ON public.lineitem (l_partkey);

CREATE INDEX IF NOT EXISTS idx_lineitem_suppkey ON public.lineitem (l_suppkey);

CREATE INDEX IF NOT EXISTS idx_lineitem_orderkey ON public.lineitem (l_orderkey);

CREATE INDEX IF NOT EXISTS idx_supplier_nationkey ON public.supplier (s_nationkey);

-- Índices para auxiliar no agrupamento e ordenação
CREATE INDEX IF NOT EXISTS idx_orders_o_orderdate_year ON public.orders (EXTRACT(YEAR FROM o_orderdate));

CREATE INDEX IF NOT EXISTS idx_nation_name ON public.nation (n_name);
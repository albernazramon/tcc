-- Índice composto para lineitem
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate_suppkey ON public.lineitem (l_shipdate, l_suppkey);

-- Índice para supplier
CREATE INDEX IF NOT EXISTS idx_supplier_suppkey ON public.supplier (s_suppkey);
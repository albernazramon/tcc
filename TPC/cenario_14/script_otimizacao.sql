-- Índice composto para lineitem
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate_partkey ON public.lineitem (l_shipdate, l_partkey);

-- Índice composto para part
CREATE INDEX IF NOT EXISTS idx_part_partkey_type ON public.part (p_partkey, p_type);
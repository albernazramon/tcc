-- Índice composto para a tabela part
CREATE INDEX IF NOT EXISTS idx_part_brand_container_partkey ON public.part (p_brand, p_container, p_partkey);

-- Índice composto para a tabela lineitem
CREATE INDEX IF NOT EXISTS idx_lineitem_partkey_quantity ON public.lineitem (l_partkey, l_quantity);
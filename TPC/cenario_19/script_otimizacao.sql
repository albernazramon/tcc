-- Índice composto para a tabela part
CREATE INDEX IF NOT EXISTS idx_part_brand_container_size_partkey ON public.part (p_brand, p_container, p_size, p_partkey);

-- Índice de cobertura para a tabela lineitem
CREATE INDEX IF NOT EXISTS idx_lineitem_ship_qty_partkey_covering
ON public.lineitem (l_shipinstruct, l_shipmode, l_quantity, l_partkey)
INCLUDE (l_extendedprice, l_discount);
-- Índice para otimizar o JOIN
CREATE INDEX IF NOT EXISTS idx_orders_o_orderkey ON public.orders (o_orderkey);

-- Índice composto para filtros, JOIN e ordenação
CREATE INDEX IF NOT EXISTS idx_lineitem_optimized ON public.lineitem (l_shipmode, l_receiptdate, l_commitdate, l_shipdate, l_orderkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate_discount_quantity
ON public.lineitem (l_shipdate, l_discount, l_quantity);
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate_returnflag_linestatus
ON public.lineitem (l_shipdate, l_returnflag, l_linestatus);
-- Índice funcional e parcial na Tabela customer
CREATE INDEX IF NOT EXISTS idx_customer_cntrycode_acctbal
ON public.customer (substring(c_phone FROM 1 FOR 2), c_acctbal)
WHERE c_acctbal > 0.00;

-- Índice na Tabela orders
CREATE INDEX IF NOT EXISTS idx_orders_custkey ON public.orders (o_custkey);
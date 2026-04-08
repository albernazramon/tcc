-- Índice para a tabela orders: filtra por data e otimiza junções
CREATE INDEX IF NOT EXISTS idx_orders_date_key_cust ON public.orders (o_orderdate, o_orderkey, o_custkey);

-- Índice para a tabela lineitem: filtra por returnflag, otimiza junção e cobre colunas para SUM
CREATE INDEX IF NOT EXISTS idx_lineitem_orderkey_returnflag_price_discount ON public.lineitem (l_orderkey, l_returnflag, l_extendedprice, l_discount);

-- Índice para a tabela customer: otimiza junções
CREATE INDEX IF NOT EXISTS idx_customer_custkey_nationkey ON public.customer (c_custkey, c_nationkey);

-- Índice para a tabela nation: otimiza junção
CREATE INDEX IF NOT EXISTS idx_nation_nationkey ON public.nation (n_nationkey);
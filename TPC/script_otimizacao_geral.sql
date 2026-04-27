-- SCRIPT DE OTIMIZACAO GERAL --

-- Cenario 1 --
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate_returnflag_linestatus
ON public.lineitem (l_shipdate, l_returnflag, l_linestatus);

-- Cenario 2 --
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_supplier_nationkey ON public.supplier (s_nationkey);
CREATE INDEX IF NOT EXISTS idx_nation_regionkey ON public.nation (n_regionkey);
CREATE INDEX IF NOT EXISTS idx_region_rname ON public.region (r_name);
CREATE INDEX IF NOT EXISTS idx_part_psize ON public.part (p_size);
CREATE INDEX IF NOT EXISTS idx_partsupp_partkey_supplycost ON public.partsupp (ps_partkey, ps_supplycost);
CREATE INDEX IF NOT EXISTS idx_supplier_acctbal_name ON public.supplier (s_acctbal DESC, s_name ASC);
CREATE INDEX IF NOT EXISTS idx_nation_name ON public.nation (n_name ASC);
CREATE INDEX IF NOT EXISTS idx_part_partkey ON public.part (p_partkey ASC);
CREATE INDEX IF NOT EXISTS idx_part_ptype_trgm ON public.part USING GIN (p_type gin_trgm_ops);

-- Cenario 3 --
CREATE INDEX IF NOT EXISTS idx_customer_mktsegment ON public.customer (c_mktsegment);
CREATE INDEX IF NOT EXISTS idx_customer_custkey ON public.customer (c_custkey);
CREATE INDEX IF NOT EXISTS idx_orders_custkey ON public.orders (o_custkey);
CREATE INDEX IF NOT EXISTS idx_orders_orderkey ON public.orders (o_orderkey);
CREATE INDEX IF NOT EXISTS idx_orders_orderdate_shippriority ON public.orders (o_orderdate, o_shippriority);
CREATE INDEX IF NOT EXISTS idx_lineitem_orderkey_shipdate_include_price_discount ON public.lineitem (l_orderkey, l_shipdate)
INCLUDE (l_extendedprice, l_discount);

-- Cenario 4 --
CREATE INDEX IF NOT EXISTS idx_lineitem_commit_receipt_orderkey ON lineitem (l_commitdate, l_receiptdate, l_orderkey);
CREATE INDEX IF NOT EXISTS idx_orders_date_priority_key ON orders (o_orderdate, o_orderpriority, o_orderkey);

-- Cenario 5 --
CREATE INDEX IF NOT EXISTS idx_orders_o_orderdate ON public.orders (o_orderdate);
CREATE INDEX IF NOT EXISTS idx_customer_c_nationkey ON public.customer (c_nationkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_l_orderkey ON public.lineitem (l_orderkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_l_suppkey ON public.lineitem (l_suppkey);

-- Cenario 6 --
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate_discount_quantity
ON public.lineitem (l_shipdate, l_discount, l_quantity);

-- Cenario 7 --
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate ON public.lineitem (l_shipdate);
CREATE INDEX IF NOT EXISTS idx_nation_name ON public.nation (n_name);

-- Cenario 8 --
CREATE INDEX IF NOT EXISTS idx_part_p_type ON public.part (p_type);
CREATE INDEX IF NOT EXISTS idx_lineitem_l_partkey ON public.lineitem (l_partkey);

-- Cenario 9 --
CREATE INDEX IF NOT EXISTS idx_part_p_name_trgm ON public.part USING GIN (p_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_orders_o_orderdate_year ON public.orders (EXTRACT(YEAR FROM o_orderdate));

-- Cenario 10 --
CREATE INDEX IF NOT EXISTS idx_orders_date_key_cust ON public.orders (o_orderdate, o_orderkey, o_custkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_orderkey_returnflag_price_discount ON public.lineitem (l_orderkey, l_returnflag, l_extendedprice, l_discount);
CREATE INDEX IF NOT EXISTS idx_customer_custkey_nationkey ON public.customer (c_custkey, c_nationkey);
CREATE INDEX IF NOT EXISTS idx_nation_nationkey ON public.nation (n_nationkey);

-- Cenario 11 --
CREATE INDEX IF NOT EXISTS idx_supplier_nkey_skey ON supplier (s_nationkey, s_suppkey);
CREATE INDEX IF NOT EXISTS idx_partsupp_skey_pkey_include ON partsupp (ps_suppkey, ps_partkey) INCLUDE (ps_supplycost, ps_availqty);

-- Cenario 12 --
CREATE INDEX IF NOT EXISTS idx_lineitem_optimized ON public.lineitem (l_shipmode, l_receiptdate, l_commitdate, l_shipdate, l_orderkey);

-- Cenario 13 --
CREATE INDEX IF NOT EXISTS idx_orders_o_comment_trgm ON orders USING GIN (o_comment gin_trgm_ops);

-- Cenario 14 --
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate_partkey ON public.lineitem (l_shipdate, l_partkey);
CREATE INDEX IF NOT EXISTS idx_part_partkey_type ON public.part (p_partkey, p_type);

-- Cenario 15 --
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate_suppkey ON public.lineitem (l_shipdate, l_suppkey);
CREATE INDEX IF NOT EXISTS idx_supplier_suppkey ON public.supplier (s_suppkey);

-- Cenario 16 --
CREATE INDEX IF NOT EXISTS idx_supplier_s_comment_trgm ON public.supplier USING GIN (s_comment gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_part_brand_type_size ON public.part (p_brand, p_type, p_size);
CREATE INDEX IF NOT EXISTS idx_partsupp_suppkey ON public.partsupp (ps_suppkey);

-- Cenario 17 --
CREATE INDEX IF NOT EXISTS idx_part_brand_container_partkey ON public.part (p_brand, p_container, p_partkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_partkey_quantity ON public.lineitem (l_partkey, l_quantity);

-- Cenario 18 --
CREATE INDEX IF NOT EXISTS idx_lineitem_orderkey_quantity ON public.lineitem (l_orderkey, l_quantity);
CREATE INDEX IF NOT EXISTS idx_orders_totalprice_date_custkey_orderkey ON public.orders (o_totalprice DESC, o_orderdate, o_custkey, o_orderkey);

-- Cenario 19 --
CREATE INDEX IF NOT EXISTS idx_part_brand_container_size_partkey ON public.part (p_brand, p_container, p_size, p_partkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_ship_qty_partkey_covering
ON public.lineitem (l_shipinstruct, l_shipmode, l_quantity, l_partkey)
INCLUDE (l_extendedprice, l_discount);

-- Cenario 20 --
CREATE INDEX IF NOT EXISTS idx_part_p_name ON public.part (p_name);
CREATE INDEX IF NOT EXISTS idx_partsupp_ps_suppkey_ps_partkey ON public.partsupp (ps_suppkey, ps_partkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_shipdate_partkey_suppkey ON public.lineitem (l_shipdate, l_partkey, l_suppkey);

-- Cenario 21 --
CREATE INDEX IF NOT EXISTS idx_orders_orderstatus ON orders (o_orderstatus);
CREATE INDEX IF NOT EXISTS idx_lineitem_composite ON lineitem (l_orderkey, l_suppkey, l_receiptdate, l_commitdate);

-- Cenario 22 --
CREATE INDEX IF NOT EXISTS idx_customer_cntrycode_acctbal
ON public.customer (substring(c_phone FROM 1 FOR 2), c_acctbal)
WHERE c_acctbal > 0.00;

-- Manutenção e Otimização --
ANALYZE;
REINDEX DATABASE tpc;

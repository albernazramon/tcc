-- Índices Recomendados
CREATE INDEX IF NOT EXISTS idx_nation_name ON nation (n_name);

CREATE INDEX IF NOT EXISTS idx_nation_nkey ON nation (n_nationkey);

CREATE INDEX IF NOT EXISTS idx_supplier_nkey_skey ON supplier (s_nationkey, s_suppkey);

CREATE INDEX IF NOT EXISTS idx_partsupp_skey_pkey_include ON partsupp (ps_suppkey, ps_partkey) INCLUDE (ps_supplycost, ps_availqty);
-- Habilita a extensão pg_trgm para índices de texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Índices para chaves estrangeiras e condições de junção/filtro
CREATE INDEX IF NOT EXISTS idx_supplier_nationkey ON public.supplier (s_nationkey);

CREATE INDEX IF NOT EXISTS idx_nation_regionkey ON public.nation (n_regionkey);

CREATE INDEX IF NOT EXISTS idx_region_rname ON public.region (r_name);

CREATE INDEX IF NOT EXISTS idx_part_psize ON public.part (p_size);

-- Índice para a CTE MinSupplyCost e condição de junção
CREATE INDEX IF NOT EXISTS idx_partsupp_partkey_supplycost ON public.partsupp (ps_partkey, ps_supplycost);

-- Índices para a cláusula ORDER BY e LIMIT
CREATE INDEX IF NOT EXISTS idx_supplier_acctbal_name ON public.supplier (s_acctbal DESC, s_name ASC);

CREATE INDEX IF NOT EXISTS idx_nation_name ON public.nation (n_name ASC);

CREATE INDEX IF NOT EXISTS idx_part_partkey ON public.part (p_partkey ASC);

-- Índice para a condição LIKE '%BRASS' (requer a extensão pg_trgm)
CREATE INDEX IF NOT EXISTS idx_part_ptype_trgm ON public.part USING GIN (p_type gin_trgm_ops);
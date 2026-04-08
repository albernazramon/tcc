-- Habilita a extensão pg_trgm e cria o índice GIN
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_supplier_s_comment_trgm ON public.supplier USING GIN (s_comment gin_trgm_ops);

-- Índices adicionais para otimização
CREATE INDEX IF NOT EXISTS idx_part_brand_type_size ON public.part (p_brand, p_type, p_size);

CREATE INDEX IF NOT EXISTS idx_partsupp_suppkey ON public.partsupp (ps_suppkey);
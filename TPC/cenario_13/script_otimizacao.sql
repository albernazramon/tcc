-- Habilita a extensão pg_trgm e cria o índice GIN
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_orders_o_comment_trgm ON orders USING GIN (o_comment gin_trgm_ops);

-- Índice para a chave estrangeira
CREATE INDEX IF NOT EXISTS idx_orders_o_custkey ON orders (o_custkey);
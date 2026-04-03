# Consulta Otimizada

```sql
WITH MinSupplyCost AS (
    SELECT
        ps.ps_partkey,
        MIN(ps.ps_supplycost) AS min_ps_supplycost_europe
    FROM
        public.partsupp ps
    JOIN
        public.supplier s ON ps.ps_suppkey = s.s_suppkey
    JOIN
        public.nation n ON s.s_nationkey = n.n_nationkey
    JOIN
        public.region r ON n.n_regionkey = r.r_regionkey
    WHERE
        r.r_name = 'EUROPE'
    GROUP BY
        ps.ps_partkey
)
SELECT
    s.s_acctbal,
    s.s_name,
    n.n_name,
    p.p_partkey,
    p.p_mfgr,
    s.s_address,
    s.s_phone,
    s.s_comment
FROM
    public.part p
JOIN
    public.partsupp ps ON p.p_partkey = ps.ps_partkey
JOIN
    public.supplier s ON s.s_suppkey = ps.ps_suppkey
JOIN
    public.nation n ON s.s_nationkey = n.n_nationkey
JOIN
    public.region r ON n.n_regionkey = r.r_regionkey
JOIN
    MinSupplyCost msc ON ps.ps_partkey = msc.ps_partkey AND ps.ps_supplycost = msc.min_ps_supplycost_europe
WHERE
    p.p_size = 15
    AND p.p_type LIKE '%BRASS'
    AND r.r_name = 'EUROPE'
ORDER BY
    s.s_acctbal DESC,
    n.n_name ASC,
    s.s_name ASC,
    p.p_partkey ASC
LIMIT 100;
```

# Insights e Análises

1. ANÁLISE DE PROBLEMAS
   A consulta original apresenta vários gargalos de performance que a tornam lenta, especialmente em grandes volumes de dados:

Subconsulta Correlacionada no WHERE: O problema mais significativo é a subconsulta (SELECT min(ps_supplycost) FROM ... WHERE p_partkey = ps_partkey AND ... r_name = 'EUROPE'). Esta subconsulta é correlacionada, o que significa que ela é reavaliada para cada linha processada pela consulta externa. Isso resulta em execuções repetitivas e um custo computacional muito alto, pois a subconsulta envolve múltiplas junções e filtros para cada avaliação (Conforme o manual do PostgreSQL (pág. 710)).
Condição LIKE '%BRASS' Não SARGable: A cláusula p_type LIKE '%BRASS' utiliza um padrão que começa com um curinga (%). Isso impede que um índice B-tree padrão seja utilizado de forma eficiente para filtrar a coluna p_type, pois o índice B-tree só pode ser usado para padrões ancorados no início da string (ex: LIKE 'BRASS%'). Consequentemente, o planejador será forçado a realizar um Seq Scan (varredura sequencial) na tabela part ou um Bitmap Heap Scan após uma varredura completa do índice, o que é ineficiente para grandes tabelas (Conforme o manual do PostgreSQL (pág. 493)).
Custo de Ordenação (ORDER BY com LIMIT): A consulta possui uma cláusula ORDER BY complexa com quatro colunas (s_acctbal desc, n_name, s_name, p_partkey) e um LIMIT 100. Sem um índice que cubra pelo menos as primeiras colunas da ordenação, o PostgreSQL precisará realizar uma etapa de Sort explícita em um grande conjunto de resultados intermediários antes de aplicar o LIMIT. Esta operação de ordenação pode ser muito custosa em termos de CPU e I/O, especialmente se os dados não couberem na memória (Conforme o manual do PostgreSQL (pág. 497, 569)). Um índice adequado poderia permitir que o planejador recuperasse as 100 primeiras linhas diretamente na ordem desejada, evitando a ordenação completa.
Múltiplas Junções: A consulta envolve cinco tabelas (part, supplier, partsupp, nation, region). A ordem e o tipo das junções (Nested Loop, Hash Join, Merge Join) escolhidos pelo planejador são cruciais. A complexidade da subconsulta correlacionada e a falta de índices adequados para as condições de filtro e junção podem levar a planos de execução subótimos. 2. CONSULTA OTIMIZADA
WITH MinSupplyCost AS (
SELECT
ps.ps_partkey,
MIN(ps.ps_supplycost) AS min_ps_supplycost_europe
FROM
public.partsupp ps
JOIN
public.supplier s ON ps.ps_suppkey = s.s_suppkey
JOIN
public.nation n ON s.s_nationkey = n.n_nationkey
JOIN
public.region r ON n.n_regionkey = r.r_regionkey
WHERE
r.r_name = 'EUROPE'
GROUP BY
ps.ps_partkey
)
SELECT
s.s_acctbal,
s.s_name,
n.n_name,
p.p_partkey,
p.p_mfgr,
s.s_address,
s.s_phone,
s.s_comment
FROM
public.part p
JOIN
public.partsupp ps ON p.p_partkey = ps.ps_partkey
JOIN
public.supplier s ON s.s_suppkey = ps.ps_suppkey
JOIN
public.nation n ON s.s_nationkey = n.n_nationkey
JOIN
public.region r ON n.n_regionkey = r.r_regionkey
JOIN
MinSupplyCost msc ON ps.ps_partkey = msc.ps_partkey AND ps.ps_supplycost = msc.min_ps_supplycost_europe
WHERE
p.p_size = 15
AND p.p_type LIKE '%BRASS'
AND r.r_name = 'EUROPE'
ORDER BY
s.s_acctbal DESC,
n.n_name ASC,
s.s_name ASC,
p.p_partkey ASC
LIMIT 100; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
As principais mudanças na consulta otimizada visam resolver os problemas identificados:

Eliminação da Subconsulta Correlacionada com CTE: A subconsulta correlacionada foi substituída por uma Common Table Expression (CTE) chamada MinSupplyCost. Esta CTE calcula o MIN(ps_supplycost) para cada ps_partkey de fornecedores localizados na região 'EUROPE' uma única vez. O resultado desta CTE é então materializado ou otimizado pelo planejador e unido à consulta principal. Isso transforma uma operação repetitiva em uma operação de pré-cálculo e junção, que é significativamente mais eficiente. O PostgreSQL provavelmente executará a CTE primeiro, usando Index Scans nas tabelas envolvidas e um HashAggregate para o GROUP BY e MIN. A junção entre a consulta principal e a CTE será provavelmente um Hash Join, que é eficiente para grandes conjuntos de dados.
Otimização de ORDER BY e LIMIT: A cláusula ORDER BY é crucial para o desempenho com LIMIT. Com os índices recomendados, o planejador pode usar um Index Scan na tabela supplier para obter as linhas já ordenadas por s_acctbal DESC e s_name ASC. Isso permite que o PostgreSQL comece a recuperar as 100 primeiras linhas diretamente, sem a necessidade de classificar o conjunto completo de resultados intermediários. Mesmo que a ordenação completa não possa ser satisfeita por um único índice (devido a n_name e p_partkey de outras tabelas), o LIMIT em conjunto com um índice inicial de ordenação reduz drasticamente o volume de dados a serem classificados, possivelmente utilizando um Incremental Sort (Conforme o manual do PostgreSQL (pág. 497, 569)).
Tratamento da Condição LIKE '%BRASS': Para otimizar a condição p_type LIKE '%BRASS', que não é SARGable para índices B-tree, a recomendação é utilizar um índice GIN (ou GIST) com a extensão pg_trgm. Este tipo de índice é projetado especificamente para pesquisas de similaridade e padrões com curingas no início ou no meio da string, permitindo um Index Scan eficiente em vez de um Seq Scan (Conforme o manual do PostgreSQL (pág. 2973, 2974)).
Plano de Execução Estimado:

Execução da CTE MinSupplyCost:

Index Scan na tabela region usando idx_region_rname para encontrar r_name = 'EUROPE'.
Nested Loop Join ou Hash Join com nation usando idx_nation_regionkey.
Nested Loop Join ou Hash Join com supplier usando idx_supplier_nationkey.
Nested Loop Join ou Hash Join com partsupp usando idx_partsupp_suppkey.
HashAggregate para agrupar por ps_partkey e calcular MIN(ps_supplycost).
O resultado da CTE será armazenado temporariamente ou otimizado para ser usado na junção principal.
Execução da Consulta Principal:

Index Scan na tabela supplier usando idx_supplier_acctbal_name para obter as linhas em ordem de s_acctbal DESC, s_name ASC.
Nested Loop Join com nation usando idx_nation_name e idx_nation_regionkey, filtrando r_name = 'EUROPE' via idx_region_rname.
Nested Loop Join com partsupp usando pk_partsupp ou idx_partsupp_suppkey.
Nested Loop Join com part usando pk_part, idx_part_psize (para p_size = 15) e idx_part_ptype_trgm (para p_type LIKE '%BRASS').
Hash Join com o resultado da CTE MinSupplyCost na condição ps.ps_partkey = msc.ps_partkey AND ps.ps_supplycost = msc.min_ps_supplycost_europe.
Aplicação do LIMIT 100 após a obtenção das primeiras 100 linhas ordenadas. Se o índice de ordenação não cobrir todas as colunas, um Sort final será aplicado, mas em um conjunto de dados muito menor.
Recomendações de Índices:

Para maximizar o desempenho da consulta otimizada, os seguintes índices são cruciais. Assumimos que as chaves primárias já possuem índices únicos.

-- Habilita a extensão pg_trgm para índices de texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Índices para chaves estrangeiras e condições de junção/filtro
CREATE INDEX IF NOT EXISTS idx_supplier_nationkey ON public.supplier (s_nationkey);
CREATE INDEX IF NOT EXISTS idx_nation_regionkey ON public.nation (n_regionkey);
CREATE INDEX IF NOT EXISTS idx_region_rname ON public.region (r_name);
CREATE INDEX IF NOT EXISTS idx_part_psize ON public.part (p_size);

-- Índice para a CTE MinSupplyCost e condição de junção
-- Este índice é crucial para o GROUP BY e MIN na CTE, e para a junção final
CREATE INDEX IF NOT EXISTS idx_partsupp_partkey_supplycost ON public.partsupp (ps_partkey, ps_supplycost);

-- Índices para a cláusula ORDER BY e LIMIT
-- Este índice é vital para a performance do ORDER BY ... LIMIT
CREATE INDEX IF NOT EXISTS idx_supplier_acctbal_name ON public.supplier (s_acctbal DESC, s_name ASC);
-- Índices adicionais para as colunas de ordenação de outras tabelas, se não forem PKs
CREATE INDEX IF NOT EXISTS idx_nation_name ON public.nation (n_name ASC);
CREATE INDEX IF NOT EXISTS idx_part_partkey ON public.part (p_partkey ASC);

-- Índice para a condição LIKE '%BRASS' (requer a extensão pg_trgm)
-- Este índice permite buscas eficientes com curingas no início do padrão
CREATE INDEX IF NOT EXISTS idx_part_ptype_trgm ON public.part USING GIN (p_type gin_trgm_ops);
Recomendações de Manutenção:

VACUUM ANALYZE: Execute VACUUM ANALYZE regularmente em todas as tabelas envolvidas (part, supplier, partsupp, nation, region). Isso garante que as estatísticas do planejador estejam sempre atualizadas, permitindo que o otimizador escolha o plano de execução mais eficiente. Estatísticas desatualizadas podem levar a escolhas de plano subótimas, como Seq Scans desnecessários.
REINDEX: Se as tabelas sofrerem muitas operações de INSERT, UPDATE ou DELETE, os índices podem se tornar fragmentados. Um REINDEX periódico pode ser benéfico para melhorar a eficiência do acesso ao índice, embora o PostgreSQL seja geralmente bom em gerenciar a fragmentação.

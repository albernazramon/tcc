# Consulta Otimizada

```sql
WITH problematic_suppliers AS (
    SELECT
        s_suppkey
    FROM
        supplier
    WHERE
        s_comment LIKE '%Customer%Complaints%'
)
SELECT
    p.p_brand,
    p.p_type,
    p.p_size,
    count(DISTINCT ps.ps_suppkey) AS supplier_cnt
FROM
    part p
JOIN
    partsupp ps ON p.p_partkey = ps.ps_partkey
LEFT JOIN
    problematic_suppliers psup ON ps.ps_suppkey = psup.s_suppkey
WHERE
    p.p_brand <> 'Brand#45'
    AND p.p_type NOT LIKE 'MEDIUM POLISHED%'
    AND p.p_size IN (49, 14, 23, 45, 19, 3, 36, 9)
    AND psup.s_suppkey IS NULL
GROUP BY
    p.p_brand,
    p.p_type,
    p.p_size
ORDER BY
    supplier_cnt DESC,
    p.p_brand,
    p.p_type,
    p.p_size;
```

# Insights e Análises

Como especialista em banco de dados PostgreSQL, analisei a consulta fornecida para identificar gargalos de performance e propor uma solução otimizada.

1. ANÁLISE DE PROBLEMAS
   A consulta original apresenta vários pontos que podem levar a um desempenho insatisfatório:

Subconsulta com NOT IN e LIKE com curinga inicial: A cláusula ps_suppkey not in (select s_suppkey from supplier where s_comment like '%Customer%Complaints%') é um dos maiores problemas.
O operador LIKE '%Customer%Complaints%' na subconsulta impede o uso de índices B-tree na coluna s_comment devido ao curinga inicial (%). Isso força um Seq Scan (varredura sequencial) completo na tabela supplier para encontrar os fornecedores com comentários correspondentes (Conforme o manual do PostgreSQL, pág. 493, índices B-tree só são eficazes para padrões LIKE ancorados no início da string).
O uso de NOT IN com uma subconsulta pode ser ineficiente, especialmente se a subconsulta retornar um grande número de linhas. Em alguns cenários, pode levar a um Hash Anti Join ou a um Nested Loop Anti Join que pode ser custoso. Embora s_suppkey seja NOT NULL, o NOT IN pode ter problemas de otimização em comparação com NOT EXISTS ou LEFT JOIN ... IS NULL.
count(distinct ps_suppkey): A agregação com DISTINCT dentro da função COUNT impede a paralelização da agregação, mesmo que outras partes da consulta pudessem ser paralelizadas (Conforme o manual do PostgreSQL, pág. 35, a agregação paralela não é suportada se a função agregada contiver DISTINCT ou ORDER BY). Isso significa que a agregação será executada em um único processo, o que pode ser um gargalo para grandes volumes de dados.
Filtros sem índices adequados:
p_brand <> 'Brand#45'
p_type not like 'MEDIUM POLISHED%'
p_size in (49, 14, 23, 45, 19, 3, 36, 9) Se não houver índices nas colunas p_brand, p_type e p_size na tabela part, o PostgreSQL pode ter que realizar um Seq Scan na tabela part para aplicar esses filtros. Embora o p_type not like 'MEDIUM POLISHED%' tenha um curinga no final, o NOT pode dificultar a otimização com um índice B-tree. O operador IN pode se beneficiar de um Bitmap Index Scan se houver um índice em p_size (Conforme o manual do PostgreSQL, pág. 31, o Bitmap Index Scan pode realizar múltiplas buscas no índice para cada valor de um predicado IN).
GROUP BY e ORDER BY: A consulta agrupa e ordena por p_brand, p_type, p_size, e também ordena por supplier_cnt DESC. Se não houver um índice que cubra essas colunas na ordem correta, o PostgreSQL precisará realizar uma etapa de Sort explícita após a agregação, o que pode ser caro para grandes conjuntos de resultados (Conforme o manual do PostgreSQL, pág. 497 e 569, um Sort explícito é provável que seja mais rápido do que usar um índice para varrer uma grande fração da tabela, mas índices são mais úteis quando poucas linhas precisam ser buscadas, especialmente com LIMIT). 2. CONSULTA OTIMIZADA
WITH problematic_suppliers AS (
SELECT
s_suppkey
FROM
supplier
WHERE
s_comment LIKE '%Customer%Complaints%'
)
SELECT
p.p_brand,
p.p_type,
p.p_size,
count(DISTINCT ps.ps_suppkey) AS supplier_cnt
FROM
part p
JOIN
partsupp ps ON p.p_partkey = ps.ps_partkey
LEFT JOIN
problematic_suppliers psup ON ps.ps_suppkey = psup.s_suppkey
WHERE
p.p_brand <> 'Brand#45'
AND p.p_type NOT LIKE 'MEDIUM POLISHED%'
AND p.p_size IN (49, 14, 23, 45, 19, 3, 36, 9)
AND psup.s_suppkey IS NULL
GROUP BY
p.p_brand,
p.p_type,
p.p_size
ORDER BY
supplier_cnt DESC,
p.p_brand,
p.p_type,
p.p_size; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
Explicação das Mudanças:

A principal mudança foi a substituição da subconsulta NOT IN por uma Common Table Expression (CTE) chamada problematic_suppliers e um LEFT JOIN subsequente com uma condição WHERE psup.s_suppkey IS NULL.

CTE problematic_suppliers: Esta CTE isola a lógica de identificação dos fornecedores problemáticos. O PostgreSQL pode optar por materializar o resultado desta CTE, o que significa que a lista de s_suppkey a serem excluídos é calculada uma vez e armazenada temporariamente.
LEFT JOIN ... IS NULL: Esta é uma técnica padrão e geralmente mais eficiente para exclusão de linhas do que NOT IN, especialmente quando a subconsulta pode retornar NULL (embora não seja o caso aqui, s_suppkey é NOT NULL) ou um grande número de linhas. O otimizador de consultas do PostgreSQL tende a lidar melhor com LEFT JOIN e IS NULL do que com NOT IN em muitos cenários, permitindo planos de execução mais previsíveis e eficientes, como Hash Join ou Merge Join.
Impacto no Plano de Execução Estimado:

problematic_suppliers CTE:

O PostgreSQL provavelmente executará um Seq Scan na tabela supplier para aplicar o filtro s_comment LIKE '%Customer%Complaints%', pois o curinga inicial impede o uso de um índice B-tree.
Se a extensão pg_trgm estiver instalada e um índice GIN ou GiST for criado em s_comment, um Index Scan ou Bitmap Index Scan poderia ser usado para essa parte, melhorando drasticamente a performance da CTE.
O resultado da CTE (a lista de s_suppkey problemáticos) pode ser materializado em memória ou em disco, dependendo do seu tamanho e das configurações de memória do servidor.
Junção part e partsupp:

A junção p.p_partkey = ps.ps_partkey é uma junção de igualdade. Com índices adequados em p.p_partkey (chave primária) e ps.ps_partkey (chave estrangeira), o planejador pode escolher um Hash Join (se uma das tabelas for pequena ou se os dados forem grandes e bem distribuídos) ou um Merge Join (se os dados já estiverem ordenados ou puderem ser ordenados eficientemente por índices) ou até um Nested Loop Join (se uma das tabelas for muito pequena após os filtros).
Filtros em part:

Os filtros p.p_brand <> 'Brand#45', p.p_type NOT LIKE 'MEDIUM POLISHED%' e p.p_size IN (...) serão aplicados. Se houver índices compostos ou múltiplos índices nas colunas p_brand, p_type e p_size, o planejador pode usar Bitmap Index Scans combinados para filtrar as linhas da tabela part de forma eficiente antes da junção (Conforme o manual do PostgreSQL, pág. 497 e 498, o sistema pode combinar múltiplos índices usando condições AND e OR através de varreduras de índice, criando um bitmap em memória).
LEFT JOIN com problematic_suppliers:

O resultado da junção part e partsupp será unido com a lista de problematic_suppliers. Se a lista de fornecedores problemáticos for pequena, um Hash Join ou Nested Loop Join pode ser usado. A condição psup.s_suppkey IS NULL filtrará as linhas onde o ps_suppkey corresponde a um fornecedor problemático.
Agregação e Ordenação:

A agregação count(DISTINCT ps.ps_suppkey) será realizada. Devido ao DISTINCT, esta etapa não será paralelizada e provavelmente envolverá um HashAggregate ou GroupAggregate com uma etapa de ordenação interna para lidar com a unicidade.
Finalmente, o resultado será ordenado por supplier_cnt DESC, p_brand, p.p_type, p.p_size. Como supplier_cnt é um valor agregado, o PostgreSQL precisará de uma etapa de Sort explícita para ordenar o resultado final, a menos que o GROUP BY e o ORDER BY pudessem ser satisfeitos por um índice que cubra as colunas de agrupamento e a ordem de agregação, o que é improvável para supplier_cnt DESC.
Recomendações de Índices:

Para maximizar a performance, os seguintes índices são recomendados:

part:

CREATE INDEX idx_part_partkey ON public.part (p_partkey); (Se não for PK)
CREATE INDEX idx_part_brand_type_size ON public.part (p_brand, p_type, p_size);
Este índice composto pode ajudar a otimizar os filtros p_brand <> 'Brand#45', p_type NOT LIKE 'MEDIUM POLISHED%' e p_size IN (...), e também pode auxiliar no GROUP BY e ORDER BY para as colunas p_brand, p_type, p_size.
partsupp:

CREATE INDEX idx_partsupp_partkey ON public.partsupp (ps_partkey); (Para o JOIN com part)
CREATE INDEX idx_partsupp_suppkey ON public.partsupp (ps_suppkey); (Para a agregação count(DISTINCT ps_suppkey) e o LEFT JOIN com problematic_suppliers)
supplier:

CREATE INDEX idx_supplier_suppkey ON public.supplier (s_suppkey); (Para o LEFT JOIN com problematic_suppliers)
Para otimizar s_comment LIKE '%Customer%Complaints%', um índice B-tree não é eficaz. É necessário usar a extensão pg_trgm e criar um índice GIN ou GiST:
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_supplier_s_comment_trgm ON public.supplier USING GIN (s_comment gin_trgm_ops);
Este índice permitirá que o LIKE com curinga inicial utilize o índice, transformando o Seq Scan em um Index Scan ou Bitmap Index Scan para a CTE problematic_suppliers (Conforme o manual do PostgreSQL, pág. 2973 e 2974, índices GIN e GiST com pg_trgm são eficazes para buscas de similaridade e padrões LIKE com curingas).
Recomendações de Manutenção:

VACUUM ANALYZE: É crucial executar VACUUM ANALYZE regularmente em todas as tabelas envolvidas (part, partsupp, supplier). Isso garante que as estatísticas do planejador de consultas estejam atualizadas, permitindo que ele faça escolhas ótimas sobre quais índices usar e qual plano de execução seguir (Conforme o manual do PostgreSQL, pág. 586, é aconselhável criar objetos de estatísticas ndistinct apenas em combinações de colunas que são realmente usadas para agrupamento e para as quais a subestimação do número de grupos resulta em planos ruins). Estatísticas precisas são fundamentais para o desempenho da consulta.

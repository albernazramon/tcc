# Consulta Otimizada

```sql
SELECT
    s.s_name,
    s.s_address
FROM
    supplier s
JOIN
    nation n ON s.s_nationkey = n.n_nationkey
JOIN
    partsupp ps ON s.s_suppkey = ps.ps_suppkey
JOIN
    part p ON ps.ps_partkey = p.p_partkey
JOIN (
    SELECT
        l_partkey,
        l_suppkey,
        0.5 * SUM(l_quantity) AS half_sum_quantity
    FROM
        lineitem
    WHERE
        l_shipdate >= DATE '1994-01-01'
        AND l_shipdate < DATE '1995-01-01'
    GROUP BY
        l_partkey,
        l_suppkey
) AS li_agg ON ps.ps_partkey = li_agg.l_partkey AND ps.ps_suppkey = li_agg.l_suppkey
WHERE
    n.n_name = 'CANADA'
    AND p.p_name LIKE 'forest%'
    AND ps.ps_availqty > li_agg.half_sum_quantity
ORDER BY
    s.s_name;
```

# Insights e Análises

1. ANÁLISE DE PROBLEMAS
   A consulta original apresenta vários pontos de ineficiência que podem levar a um desempenho lento:

Subconsultas Correlacionadas e Aninhadas:

A estrutura da consulta é baseada em múltiplas subconsultas aninhadas com o operador IN. Embora o otimizador do PostgreSQL possa, em alguns casos, reescrever subconsultas IN para junções (semi-joins), a profundidade e a correlação das subconsultas podem dificultar essa otimização.
O maior problema reside na subconsulta escalar correlacionada dentro da cláusula WHERE da tabela partsupp:
ps_availqty > (
select 0.5 \* sum(l_quantity)
from lineitem
where l_partkey = ps_partkey
and l_suppkey = ps_suppkey
and l_shipdate >= date '1994-01-01'
and l_shipdate < date '1994-01-01' + interval '1 year'
)
Esta subconsulta é "correlacionada" porque suas condições (l_partkey = ps_partkey e l_suppkey = ps_suppkey) dependem das colunas da consulta externa (partsupp). Isso significa que a subconsulta é reavaliada para cada linha processada da tabela partsupp. Se partsupp tiver um grande número de linhas, isso resultará em um número massivo de execuções da subconsulta, cada uma potencialmente realizando um scan ou busca de índice na tabela lineitem e uma agregação (SUM), o que é extremamente custoso em termos de CPU e I/O.
Filtro LIKE 'forest%':

A condição p_name LIKE 'forest%' é SARGable, o que significa que pode se beneficiar de um índice B-tree na coluna p_name (Conforme o manual do PostgreSQL, pág. 493). No entanto, sem um índice adequado, esta condição exigirá um Seq Scan completo na tabela part, que é ineficiente para tabelas grandes.
Junções Implícitas:

A cláusula FROM supplier, nation WHERE s_nationkey = n_nationkey utiliza a sintaxe de junção implícita (vírgula). Embora o otimizador do PostgreSQL trate isso como uma INNER JOIN, a sintaxe explícita é geralmente preferida por clareza e consistência, e pode, em alguns casos, auxiliar o otimizador.
Custo de Ordenação (ORDER BY s_name):

A consulta final exige que os resultados sejam ordenados por s_name. Se o plano de execução não conseguir produzir os resultados já na ordem desejada (por exemplo, através de um Index Scan que corresponda à ordem), o PostgreSQL terá que realizar uma etapa de Sort explícita. Para grandes conjuntos de resultados, essa operação de ordenação pode ser intensiva em CPU e I/O, potencialmente exigindo escrita para disco se a memória disponível for insuficiente (Conforme o manual do PostgreSQL, pág. 497, 569). 2. CONSULTA OTIMIZADA
SELECT
s.s_name,
s.s_address
FROM
supplier s
JOIN
nation n ON s.s_nationkey = n.n_nationkey
JOIN
partsupp ps ON s.s_suppkey = ps.ps_suppkey
JOIN
part p ON ps.ps_partkey = p.p_partkey
JOIN (
SELECT
l_partkey,
l_suppkey,
0.5 \* SUM(l_quantity) AS half_sum_quantity
FROM
lineitem
WHERE
l_shipdate >= DATE '1994-01-01'
AND l_shipdate < DATE '1995-01-01'
GROUP BY
l_partkey,
l_suppkey
) AS li_agg ON ps.ps_partkey = li_agg.l_partkey AND ps.ps_suppkey = li_agg.l_suppkey
WHERE
n.n_name = 'CANADA'
AND p.p_name LIKE 'forest%'
AND ps.ps_availqty > li_agg.half_sum_quantity
ORDER BY
s.s_name; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
As principais modificações na consulta otimizada visam eliminar as subconsultas correlacionadas e aninhadas, substituindo-as por junções explícitas e uma agregação prévia, o que permite ao otimizador do PostgreSQL construir um plano de execução muito mais eficiente.

Mudanças Realizadas:

Eliminação da Subconsulta Correlacionada: A subconsulta escalar correlacionada em lineitem foi reescrita como uma subconsulta derivada (li_agg). Esta subconsulta calcula 0.5 * SUM(l_quantity) para cada par (l_partkey, l_suppkey) uma única vez, após filtrar as linhas por l_shipdate. O resultado dessa agregação é então unido à tabela partsupp. Essa transformação é crucial, pois converte uma operação potencialmente N*M (N execuções da subconsulta para M linhas de partsupp) em uma única agregação seguida por uma junção, reduzindo drasticamente o custo computacional.
Substituição de IN por INNER JOIN: Todas as subconsultas IN foram substituídas por INNER JOINs explícitas. Isso permite que o otimizador do PostgreSQL utilize algoritmos de junção mais eficientes (como Hash Join, Merge Join ou Nested Loop Join) e aplique filtros mais cedo no plano de execução, reduzindo o volume de dados a serem processados em etapas posteriores.
Junções Explícitas: A sintaxe de junção implícita (FROM t1, t2 WHERE t1.id = t2.id) foi substituída por INNER JOIN ... ON .... Embora o otimizador geralmente trate ambas as formas de forma semelhante, a sintaxe explícita melhora a clareza e a manutenibilidade da consulta.
Plano de Execução Estimado:

O PostgreSQL provavelmente processará a nova consulta da seguinte forma:

Execução da Subconsulta li_agg:
O otimizador iniciará com um Index Scan na tabela lineitem usando um índice em (l_shipdate, l_partkey, l_suppkey) para filtrar as datas (l_shipdate >= '1994-01-01' AND l_shipdate < '1995-01-01').
Em seguida, realizará um HashAggregate ou GroupAggregate sobre os resultados filtrados para calcular 0.5 \* SUM(l_quantity) agrupado por l_partkey e l_suppkey. O resultado será materializado ou transmitido para a próxima etapa.
Junções e Filtros:
A consulta pode começar com um Index Scan na tabela nation para encontrar n_name = 'CANADA', seguido por um Nested Loop Join ou Hash Join com supplier usando s_nationkey = n_nationkey.
Em paralelo, ou em uma etapa subsequente, um Index Scan na tabela part para p_name LIKE 'forest%' será realizado.
Os resultados de supplier (filtrados por nation) e part (filtrados por p_name) serão unidos com partsupp usando s_suppkey = ps_suppkey e ps_partkey = p_partkey.
Finalmente, o resultado dessas junções será unido com a subconsulta agregada li_agg usando ps.ps_partkey = li_agg.l_partkey AND ps.ps_suppkey = li_agg.l_suppkey. A condição ps.ps_availqty > li_agg.half_sum_quantity será aplicada durante esta junção.
A ordem das junções será determinada pelo otimizador com base nas estatísticas e na seletividade dos filtros, buscando reduzir o número de linhas o mais cedo possível.
Ordenação Final:
A cláusula ORDER BY s.s_name será aplicada. Se um Index Scan em supplier (usando um índice em s_name) puder ser o ponto de partida da consulta e os filtros subsequentes não quebrarem a ordem, a etapa de Sort pode ser evitada (Conforme o manual do PostgreSQL, pág. 497, 569). Caso contrário, um Sort explícito será realizado sobre o conjunto de resultados final.
Impacto Previsto: A principal melhoria será a eliminação da execução repetitiva da subconsulta correlacionada, transformando-a em uma agregação única. Isso mudará o plano de execução de múltiplos Nested Loops caros para uma série de Hash Joins ou Merge Joins mais eficientes, com Index Scans sendo utilizados para filtros e junções, onde índices apropriados existirem. O custo total da consulta será drasticamente reduzido.

Recomendações de Índices:

Para garantir a máxima performance da consulta otimizada, os seguintes índices são cruciais:

part.p_name: Para a condição p_name LIKE 'forest%'.

CREATE INDEX idx_part_p_name ON public.part (p_name);
-- Se o locale do banco de dados não for 'C' e houver problemas de performance com LIKE,
-- considere um índice com operador de classe específico para padrões:
-- CREATE INDEX idx_part_p_name_pattern ON public.part (p_name varchar_pattern_ops);
(Conforme o manual do PostgreSQL, pág. 493, 505)

nation.n_name: Para a condição n_name = 'CANADA'.

CREATE INDEX idx_nation_n_name ON public.nation (n_name);
supplier.s_nationkey: Para a junção com nation.

CREATE INDEX idx_supplier_s_nationkey ON public.supplier (s_nationkey);
supplier.s_suppkey: Para a junção com partsupp.

CREATE INDEX idx_supplier_s_suppkey ON public.supplier (s_suppkey);
partsupp.ps_suppkey e partsupp.ps_partkey: Para as junções com supplier, part e li_agg. Um índice composto é ideal.

CREATE INDEX idx_partsupp_ps_suppkey_ps_partkey ON public.partsupp (ps_suppkey, ps_partkey);
-- Ou, dependendo da seletividade e ordem de junção:
-- CREATE INDEX idx_partsupp_ps_partkey_ps_suppkey ON public.partsupp (ps_partkey, ps_suppkey);
part.p_partkey: Para a junção com partsupp.

CREATE INDEX idx_part_p_partkey ON public.part (p_partkey);
lineitem.l_shipdate, l_partkey, l_suppkey: Para a subconsulta li_agg. Um índice composto que inclua as colunas de filtro e agrupamento é crucial. A ordem das colunas no índice é importante para otimizar o filtro de range e o agrupamento.

CREATE INDEX idx_lineitem_shipdate_partkey_suppkey ON public.lineitem (l_shipdate, l_partkey, l_suppkey);
supplier.s_name: Para a cláusula ORDER BY. Um índice nesta coluna pode permitir que o PostgreSQL evite uma etapa de ordenação explícita se puder iniciar o plano de execução com um Index Scan em supplier que já produza os resultados em ordem (Conforme o manual do PostgreSQL, pág. 497, 569).

CREATE INDEX idx_supplier_s_name ON public.supplier (s_name);
Recomendações de Manutenção:

ANALYZE: Após a criação de novos índices ou após grandes modificações nos dados (INSERTs, UPDATEs, DELETEs), é fundamental executar ANALYZE em todas as tabelas envolvidas (supplier, nation, partsupp, part, lineitem). Isso garante que o otimizador tenha estatísticas atualizadas sobre a distribuição dos dados e a seletividade dos índices, permitindo-lhe gerar planos de execução mais eficientes.
VACUUM (ou AUTOVACUUM): O VACUUM é essencial para recuperar espaço em disco ocupado por tuplas mortas e para atualizar o mapa de visibilidade, o que é crucial para Index-Only Scans (se aplicável) e para a performance geral. O AUTOVACUUM deve estar habilitado e configurado adequadamente para gerenciar isso automaticamente.

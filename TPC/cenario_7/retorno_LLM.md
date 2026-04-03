# Consulta Otimizada

```sql
SELECT
    n1.n_name AS supp_nation,
    n2.n_name AS cust_nation,
    EXTRACT(YEAR FROM l.l_shipdate) AS l_year,
    SUM(l.l_extendedprice * (1 - l.l_discount)) AS revenue
FROM
    lineitem l
JOIN
    supplier s ON s.s_suppkey = l.l_suppkey
JOIN
    orders o ON o.o_orderkey = l.l_orderkey
JOIN
    customer c ON c.c_custkey = o.o_custkey
JOIN
    nation n1 ON s.s_nationkey = n1.n_nationkey
JOIN
    nation n2 ON c.c_nationkey = n2.n_nationkey
WHERE
    l.l_shipdate BETWEEN DATE '1995-01-01' AND DATE '1996-12-31'
    AND (
        (n1.n_name = 'FRANCE' AND n2.n_name = 'GERMANY')
        OR (n1.n_name = 'GERMANY' AND n2.n_name = 'FRANCE')
    )
GROUP BY
    n1.n_name,
    n2.n_name,
    l_year
ORDER BY
    n1.n_name,
    n2.n_name,
    l_year;
```

# Insights e Análises

1. ANÁLISE DE PROBLEMAS:
   A consulta original apresenta diversas ineficiências que podem levar a um desempenho lento, especialmente em bancos de dados com grandes volumes de dados, como é o caso de tabelas como lineitem. Os principais problemas são:

Ausência de Índices Adequados: O problema mais crítico é a falta de índices nas tabelas. Sem índices, o PostgreSQL é forçado a realizar varreduras sequenciais (Seq Scan) em tabelas grandes para satisfazer as condições de JOIN e WHERE.
Joins Ineficientes: As operações de JOIN entre lineitem, supplier, orders, customer e nation dependem das chaves s_suppkey, l_suppkey, o_orderkey, l_orderkey, c_custkey, o_custkey, s_nationkey, n1.n_nationkey, c_nationkey, n2.n_nationkey. Sem índices nessas colunas, o planejador de consultas provavelmente recorrerá a Nested Loop Joins com varreduras sequenciais ou Hash Joins que exigem mais memória e CPU para construir as tabelas de hash, resultando em alto custo de I/O e CPU.
Filtros Lentos: As condições l_shipdate BETWEEN date '1995-01-01' AND date '1996-12-31' e (n1.n_name = 'FRANCE' AND n2.n_name = 'GERMANY') OR (n1.n_name = 'GERMANY' AND n2.n_name = 'FRANCE') não podem ser otimizadas por varreduras de índice. A coluna l_shipdate é crucial para filtrar um subconjunto de lineitem. Sem um índice, uma varredura sequencial completa da tabela lineitem será necessária, mesmo que apenas uma pequena fração dos dados seja relevante. Da mesma forma, a filtragem por n_name na tabela nation exigirá varreduras sequenciais. Conforme o manual do PostgreSQL, índices são fundamentais para que o planejador possa usar operadores indexáveis e valores de comparação para acelerar a recuperação de dados (pág. 493.0).
Custo de Ordenação e Agregação: A consulta inclui cláusulas GROUP BY e ORDER BY idênticas (supp_nation, cust_nation, l_year). Sem índices que possam fornecer os dados já na ordem desejada, o PostgreSQL terá que realizar uma etapa explícita de Sort após a agregação (pág. 569.0). Para grandes conjuntos de resultados intermediários, essa operação de ordenação pode ser muito custosa em termos de CPU e memória, podendo até mesmo exigir despejo para disco se a memória disponível for insuficiente.
Subquery (Derived Table): Embora o otimizador do PostgreSQL seja geralmente inteligente o suficiente para "achatar" subconsultas simples como a shipping neste caso, a presença dela pode, em algumas situações, limitar as opções de otimização do planejador, especialmente se as estatísticas não forem ideais. A reescrita para JOINs explícitos pode tornar a intenção mais clara para o otimizador. 2. CONSULTA OTIMIZADA:
SELECT
n1.n_name AS supp_nation,
n2.n_name AS cust_nation,
EXTRACT(YEAR FROM l.l_shipdate) AS l_year,
SUM(l.l_extendedprice \* (1 - l.l_discount)) AS revenue
FROM
lineitem l
JOIN
supplier s ON s.s_suppkey = l.l_suppkey
JOIN
orders o ON o.o_orderkey = l.l_orderkey
JOIN
customer c ON c.c_custkey = o.o_custkey
JOIN
nation n1 ON s.s_nationkey = n1.n_nationkey
JOIN
nation n2 ON c.c_nationkey = n2.n_nationkey
WHERE
l.l_shipdate BETWEEN DATE '1995-01-01' AND DATE '1996-12-31'
AND (
(n1.n_name = 'FRANCE' AND n2.n_name = 'GERMANY')
OR (n1.n_name = 'GERMANY' AND n2.n_name = 'FRANCE')
)
GROUP BY
n1.n_name,
n2.n_name,
l_year
ORDER BY
n1.n_name,
n2.n_name,
l_year; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO:
Explicação das Mudanças:

Achatamento da Subquery: A subquery shipping foi removida e suas operações foram integradas diretamente na consulta principal usando JOINs explícitos. Embora o otimizador do PostgreSQL seja capaz de realizar essa otimização internamente, a reescrita explícita pode, em alguns casos, simplificar o trabalho do planejador e garantir que todas as otimizações de JOIN e WHERE sejam consideradas desde o início.
Uso de Aliases Consistentes: Foram utilizados aliases mais curtos e consistentes (l, s, o, c, n1, n2) para melhorar a legibilidade da consulta.
GROUP BY e ORDER BY com Nomes Originais: As colunas no GROUP BY e ORDER BY foram referenciadas pelos seus nomes originais (n1.n_name, n2.n_name, l_year) em vez dos aliases definidos na SELECT list. Embora o PostgreSQL geralmente suporte aliases na GROUP BY e ORDER BY, usar os nomes originais ou expressões pode ser mais robusto e claro.
Impacto Previsto no Plano de Execução (com Índices):

A principal melhoria de performance virá da adição de índices. Sem eles, o plano de execução seria dominado por Seq Scans e Hash Joins ou Nested Loop Joins muito caros. Com os índices propostos, o plano de execução estimado seria drasticamente diferente:

Filtro em nation: O planejador iniciaria com Index Scans na tabela nation usando idx_nation_name para encontrar as nações 'FRANCE' e 'GERMANY'. A condição OR seria tratada eficientemente através de Bitmap Index Scans que combinam os resultados de múltiplos índices (pág. 497.0, 13, 18).
Filtro em lineitem: Simultaneamente, ou como um passo inicial, um Index Scan seria realizado em lineitem usando idx_lineitem_shipdate para filtrar as linhas dentro do período 1995-01-01 e 1996-12-31. Isso reduziria drasticamente o número de linhas a serem processadas da tabela lineitem.
Joins Otimizados: Com índices nas chaves primárias e estrangeiras, os JOINs seriam transformados de Seq Scans para Index Scans ou Bitmap Heap Scans seguidos por Nested Loop Joins ou Merge Joins muito mais eficientes. Por exemplo:
lineitem seria unida a supplier usando idx_lineitem_suppkey e supplier_pkey.
lineitem seria unida a orders usando lineitem_pkey (que inclui l_orderkey) e orders_pkey.
orders seria unida a customer usando idx_orders_custkey e customer_pkey.
supplier seria unida a n1 usando idx_supplier_nationkey e nation_pkey.
customer seria unida a n2 usando idx_customer_nationkey e nation_pkey. O uso de Bitmap Heap Scans é provável para as tabelas maiores (lineitem) quando muitos índices são combinados ou quando o filtro é seletivo, pois permite visitar as linhas da tabela em ordem física, reduzindo I/O aleatório (pág. 498.0, 13).
Agregação e Ordenação: Após a filtragem e os JOINs, o conjunto de dados intermediário será significativamente menor. A agregação (SUM) e o GROUP BY seriam realizados. Como o ORDER BY é idêntico ao GROUP BY, o PostgreSQL pode, em alguns casos, evitar uma etapa de Sort explícita se a agregação já produzir os resultados na ordem desejada (pág. 496.0, 16). No entanto, devido à expressão EXTRACT(YEAR FROM l_shipdate), é provável que uma etapa de Sort ainda seja necessária, mas sobre um conjunto de dados muito menor, tornando-a muito mais rápida. O planejador pode optar por uma Hash Aggregate ou GroupAggregate seguido por um Sort.
Recomendações de Índices:

Para alcançar a performance máxima, os seguintes índices devem ser criados:

-- Índices de Chave Primária (garantem unicidade e aceleram lookups)
ALTER TABLE public.supplier ADD PRIMARY KEY (s_suppkey);
ALTER TABLE public.lineitem ADD PRIMARY KEY (l_orderkey, l_linenumber);
ALTER TABLE public.orders ADD PRIMARY KEY (o_orderkey);
ALTER TABLE public.customer ADD PRIMARY KEY (c_custkey);
ALTER TABLE public.nation ADD PRIMARY KEY (n_nationkey);

-- Índices em Chaves Estrangeiras (aceleram operações de JOIN)
CREATE INDEX idx_lineitem_suppkey ON public.lineitem (l_suppkey);
CREATE INDEX idx_orders_custkey ON public.orders (o_custkey);
CREATE INDEX idx_supplier_nationkey ON public.supplier (s_nationkey);
CREATE INDEX idx_customer_nationkey ON public.customer (c_nationkey);

-- Índices para Filtros e Ordenação
CREATE INDEX idx_lineitem_shipdate ON public.lineitem (l_shipdate);
CREATE INDEX idx_nation_name ON public.nation (n_name);
Recomendações de Manutenção:

ANALYZE: Após a criação dos índices e qualquer carregamento significativo de dados, é crucial executar ANALYZE em todas as tabelas envolvidas (supplier, lineitem, orders, customer, nation). Isso atualiza as estatísticas do planejador de consultas, permitindo que ele escolha os planos de execução mais eficientes, aproveitando os novos índices.
VACUUM (ou AUTOVACUUM): Garanta que o autovacuum esteja habilitado e configurado adequadamente. VACUUM é essencial para remover tuplas mortas, recuperar espaço em disco e atualizar o mapa de visibilidade, o que é vital para o desempenho de Index Scans e Bitmap Heap Scans.
Monitoramento: Monitore o desempenho da consulta com EXPLAIN ANALYZE após a implementação das mudanças para validar o plano de execução e identificar quaisquer gargalos remanescentes. Ajustes finos nos parâmetros de configuração do servidor (como work_mem, shared_buffers, random_page_cost, seq_page_cost - pág. 710.0, 9) podem ser necessários dependendo do ambiente e da carga de trabalho.
Reindexação Periódica: Para tabelas com alta atividade de INSERT/UPDATE/DELETE, a reindexação periódica pode ser benéfica para manter a eficiência dos índices, embora o autovacuum geralmente cuide da maioria dos problemas de fragmentação.

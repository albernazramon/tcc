# Consulta Otimizada

```sql
SELECT
    EXTRACT(YEAR FROM o.o_orderdate) AS o_year,
    SUM(CASE
        WHEN n2.n_name = 'BRAZIL' THEN l.l_extendedprice * (1 - l.l_discount)
        ELSE 0
    END) / SUM(l.l_extendedprice * (1 - l.l_discount)) AS mkt_share
FROM
    part p
JOIN
    lineitem l ON p.p_partkey = l.l_partkey
JOIN
    supplier s ON s.s_suppkey = l.l_suppkey
JOIN
    orders o ON l.l_orderkey = o.o_orderkey
JOIN
    customer c ON o.o_custkey = c.c_custkey
JOIN
    nation n1 ON c.c_nationkey = n1.n_nationkey
JOIN
    region r ON n1.n_regionkey = r.r_regionkey
JOIN
    nation n2 ON s.s_nationkey = n2.n_nationkey
WHERE
    r.r_name = 'AMERICA'
    AND o.o_orderdate BETWEEN DATE '1995-01-01' AND DATE '1996-12-31'
    AND p.p_type = 'ECONOMY ANODIZED STEEL'
GROUP BY
    o_year
ORDER BY
    o_year;
```

# Insights e Análises

ANÁLISE DE PROBLEMAS

A consulta original apresenta vários pontos que podem levar a um desempenho insatisfatório, especialmente em grandes volumes de dados:

Varreduras Sequenciais (Seq Scans) e Joins Ineficientes: A ausência de índices adequados nas colunas utilizadas nas cláusulas WHERE e ON de JOIN é a principal causa de lentidão. Sem índices, o planejador de consultas do PostgreSQL será forçado a realizar varreduras sequenciais completas em tabelas grandes para encontrar os dados correspondentes aos filtros e condições de junção. Isso é significativamente mais caro do que usar um índice para buscar linhas específicas (Conforme o manual do PostgreSQL, pág. 710, 8, 9).
Filtros Não Otimizados:
o_orderdate BETWEEN date '1995-01-01' AND date '1996-12-31': Embora esta condição seja SARGable (Search Argumentable), sem um índice na coluna o_orderdate, o PostgreSQL terá que escanear a tabela orders inteira para aplicar o filtro.
p_type = 'ECONOMY ANODIZED STEEL': Similarmente, sem um índice em p_type, a tabela part será varrida sequencialmente.
r_name = 'AMERICA': O mesmo se aplica à tabela region e à coluna r_name. A aplicação de múltiplos filtros sem índices pode levar a Bitmap Heap Scans ou Seq Scans seguidos de filtragem, que são menos eficientes do que Index Scans diretos para conjuntos de resultados pequenos ou médios (Conforme o manual do PostgreSQL, pág. 568, 8).
Custo de Ordenação e Agregação: A consulta inclui GROUP BY o_year e ORDER BY o_year. A coluna o_year é derivada da função EXTRACT(YEAR FROM o_orderdate). Se os dados de entrada para a agregação não estiverem pré-ordenados por o_orderdate (e, consequentemente, por o_year), o PostgreSQL precisará realizar uma etapa de ordenação explícita (Sort ou HashAggregate), o que pode ser custoso em termos de CPU e memória para grandes conjuntos de dados (Conforme o manual do PostgreSQL, pág. 569, 4, 15). Embora um índice em o_orderdate possa ajudar a satisfazer a ordenação (Conforme o manual do PostgreSQL, pág. 497, 15), a função EXTRACT pode impedir o uso direto do índice para o GROUP BY sem um índice funcional.
Subquery: Embora o otimizador do PostgreSQL seja inteligente e muitas vezes "achate" subconsultas simples, a estrutura com uma subconsulta pode, em alguns casos, limitar as opções do planejador ou introduzir uma pequena sobrecarga. A reescrita para JOIN explícitos geralmente oferece mais clareza e pode, em certas situações, levar a planos de execução mais diretos.
CONSULTA OTIMIZADA

SELECT
EXTRACT(YEAR FROM o.o_orderdate) AS o_year,
SUM(CASE
WHEN n2.n_name = 'BRAZIL' THEN l.l_extendedprice _ (1 - l.l_discount)
ELSE 0
END) / SUM(l.l_extendedprice _ (1 - l.l_discount)) AS mkt_share
FROM
part p
JOIN
lineitem l ON p.p_partkey = l.l_partkey
JOIN
supplier s ON s.s_suppkey = l.l_suppkey
JOIN
orders o ON l.l_orderkey = o.o_orderkey
JOIN
customer c ON o.o_custkey = c.c_custkey
JOIN
nation n1 ON c.c_nationkey = n1.n_nationkey
JOIN
region r ON n1.n_regionkey = r.r_regionkey
JOIN
nation n2 ON s.s_nationkey = n2.n_nationkey
WHERE
r.r_name = 'AMERICA'
AND o.o_orderdate BETWEEN DATE '1995-01-01' AND DATE '1996-12-31'
AND p.p_type = 'ECONOMY ANODIZED STEEL'
GROUP BY
o_year
ORDER BY
o_year;
EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO

Mudanças Realizadas:

Subconsulta Flattening (Achatamento): A subconsulta all_nations foi removida e suas operações foram integradas diretamente na cláusula FROM principal usando JOIN explícitos. Embora o otimizador do PostgreSQL seja capaz de achatar subconsultas em muitos cenários, a utilização de JOIN explícitos pode, por vezes, simplificar o trabalho do planejador e levar a planos de execução mais eficientes e previsíveis. A semântica da consulta permanece inalterada.
Impacto Previsto e Plano de Execução Estimado:

A principal melhoria de performance virá da adição de índices estratégicos. Com os índices recomendados, o PostgreSQL provavelmente processará a nova consulta da seguinte forma:

Filtros Iniciais Otimizados (Index Scans / Bitmap Index Scans):

O planejador começará utilizando Index Scan no idx_region_r_name para localizar rapidamente a linha da região 'AMERICA'.
Simultaneamente, Index Scan no idx_part_p_type será usado para encontrar as partes do tipo 'ECONOMY ANODIZED STEEL'.
Um Index Scan no idx_orders_o_orderdate será empregado para filtrar as ordens dentro do período de datas especificado.
Para múltiplas condições WHERE em diferentes tabelas, o PostgreSQL pode usar Bitmap Index Scans e combinar os resultados (AND/OR) em um bitmap na memória, que é então usado para buscar as linhas reais da tabela (Bitmap Heap Scan). Isso é mais eficiente do que varreduras sequenciais completas (Conforme o manual do PostgreSQL, pág. 497, 13, 18 e pág. 568, 8).
Junções (Joins) Eficientes:

Com índices nas chaves estrangeiras (l_partkey, l_suppkey, o_custkey, c_nationkey, n_regionkey, s_nationkey), as operações de JOIN serão significativamente mais rápidas. O planejador poderá optar por Nested Loop Joins eficientes, especialmente se os conjuntos de dados filtrados forem pequenos, ou Hash Joins se os conjuntos intermediários forem maiores, mas com acesso rápido aos dados de junção (Conforme o manual do PostgreSQL, pág. 493, 2).
A ordem das junções será determinada pelo planejador com base na seletividade dos filtros e na disponibilidade dos índices, buscando minimizar o número de linhas processadas em cada etapa.
Agregação e Ordenação (GroupAggregate / Sort):

Após a filtragem e as junções, os dados necessários para volume e nation serão calculados.
A agregação (SUM) e o agrupamento (GROUP BY o_year) serão realizados. Se o Index Scan em o_orderdate já tiver produzido os dados em ordem de data (e, portanto, de ano), o PostgreSQL poderá usar um GroupAggregate que se beneficia da entrada pré-ordenada, evitando uma etapa de ordenação explícita.
A cláusula ORDER BY o_year final também poderá ser satisfeita se a agregação já tiver produzido um resultado ordenado, ou se um Index Scan em o_orderdate for usado para a ordenação inicial (Conforme o manual do PostgreSQL, pág. 497, 15 e pág. 569, 4).
Para grandes volumes de dados, o PostgreSQL pode empregar Parallel Aggregation, onde múltiplos processos de trabalho realizam agregações parciais, e um processo líder finaliza o resultado, reduzindo o tempo total de execução (Conforme o manual do PostgreSQL, pág. 596, 20, 21).
Recomendações de Manutenção:

Para garantir a máxima performance e que o planejador de consultas utilize os índices de forma eficaz, as seguintes ações são cruciais:

Criação de Índices:

-- Índices para colunas de filtro
CREATE INDEX IF NOT EXISTS idx_orders_o_orderdate ON public.orders (o_orderdate);
CREATE INDEX IF NOT EXISTS idx_part_p_type ON public.part (p_type);
CREATE INDEX IF NOT EXISTS idx_region_r_name ON public.region (r_name);

-- Índices para chaves estrangeiras (FKs) que não são PKs ou parte de PKs compostas
-- Assumindo que as chaves primárias (PKs) já possuem índices.
CREATE INDEX IF NOT EXISTS idx_lineitem_l_partkey ON public.lineitem (l_partkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_l_suppkey ON public.lineitem (l_suppkey);
-- l_orderkey é parte da PK de lineitem, então já deve estar indexado.
CREATE INDEX IF NOT EXISTS idx_orders_o_custkey ON public.orders (o_custkey);
CREATE INDEX IF NOT EXISTS idx_customer_c_nationkey ON public.customer (c_nationkey);
CREATE INDEX IF NOT EXISTS idx_nation_n_regionkey ON public.nation (n_regionkey);
CREATE INDEX IF NOT EXISTS idx_supplier_s_nationkey ON public.supplier (s_nationkey);
Estes índices permitirão que o planejador de consultas utilize Index Scans ou Bitmap Index Scans para acessar os dados de forma muito mais eficiente, evitando varreduras sequenciais completas em tabelas grandes.

VACUUM ANALYZE Regular: É fundamental executar VACUUM ANALYZE regularmente em todas as tabelas envolvidas na consulta (part, supplier, lineitem, orders, customer, nation, region). Isso garante que as estatísticas do planejador de consultas estejam sempre atualizadas, permitindo que ele tome as melhores decisões sobre quais índices usar e qual a ordem mais eficiente para as junções e agregações. Estatísticas desatualizadas podem levar o planejador a escolher planos de execução subótimos.

Monitoramento: Monitore o plano de execução da consulta otimizada usando EXPLAIN ANALYZE para verificar se os índices estão sendo utilizados conforme o esperado e para identificar quaisquer gargalos remanescentes. Ajustes adicionais, como índices compostos ou configurações de memória (work_mem), podem ser considerados com base nos resultados reais.

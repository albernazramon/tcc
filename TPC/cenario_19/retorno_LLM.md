# Consulta Otimizada

```sql
SELECT SUM(revenue) AS revenue
FROM (
    SELECT
        l.l_extendedprice * (1 - l.l_discount) AS revenue
    FROM
        lineitem l
    JOIN
        part p ON p.p_partkey = l.l_partkey
    WHERE
        p.p_brand = 'Brand#12'
        AND p.p_container IN ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG')
        AND l.l_quantity BETWEEN 1 AND 11
        AND p.p_size BETWEEN 1 AND 5
        AND l.l_shipmode IN ('AIR', 'AIR REG')
        AND l.l_shipinstruct = 'DELIVER IN PERSON'
    UNION ALL
    SELECT
        l.l_extendedprice * (1 - l.l_discount) AS revenue
    FROM
        lineitem l
    JOIN
        part p ON p.p_partkey = l.l_partkey
    WHERE
        p.p_brand = 'Brand#23'
        AND p.p_container IN ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
        AND l.l_quantity BETWEEN 10 AND 20
        AND p.p_size BETWEEN 1 AND 10
        AND l.l_shipmode IN ('AIR', 'AIR REG')
        AND l.l_shipinstruct = 'DELIVER IN PERSON'
    UNION ALL
    SELECT
        l.l_extendedprice * (1 - l.l_discount) AS revenue
    FROM
        lineitem l
    JOIN
        part p ON p.p_partkey = l.l_partkey
    WHERE
        p.p_brand = 'Brand#34'
        AND p.p_container IN ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
        AND l.l_quantity BETWEEN 20 AND 30
        AND p.p_size BETWEEN 1 AND 15
        AND l.l_shipmode IN ('AIR', 'AIR REG')
        AND l.l_shipinstruct = 'DELIVER IN PERSON'
) AS subquery_revenue;
```

# Insights e Análises

1. ANÁLISE DE PROBLEMAS
   A consulta original apresenta problemas de performance principalmente devido à sua estrutura com múltiplas condições OR complexas, que abrangem colunas de duas tabelas (lineitem e part) e incluem uma condição de junção (p_partkey = l_partkey) dentro de cada bloco OR.

Ineficiência da Cláusula OR Complexa: Conforme o manual do PostgreSQL (pág. 497.0), uma varredura de índice única é otimizada para cláusulas de consulta unidas por AND. Uma condição OR extensa, especialmente quando envolve múltiplas colunas e tabelas, dificulta o uso eficiente de índices compostos tradicionais. O planejador de consultas pode ter dificuldade em criar um plano de execução ideal, podendo recorrer a varreduras sequenciais (Seq Scan) em uma ou ambas as tabelas, o que é custoso para tabelas grandes. Mesmo que o PostgreSQL possa combinar múltiplos índices usando bitmaps para condições OR (pág. 497.0, pág. 498.0), a complexidade da condição aninhada com ANDs e a junção pode levar a um plano de execução subótimo, onde a construção e combinação dos bitmaps se torna uma operação cara.
Junção e Filtros Distribuídos: A junção p_partkey = l_partkey é avaliada repetidamente dentro de cada um dos três blocos OR, juntamente com os filtros específicos de cada tabela. Isso pode levar a uma avaliação redundante ou a um plano de execução que não consegue otimizar a junção e os filtros de forma coesa.
Potencial para Múltiplas Varreduras de Tabela e Heap Scans: Sem índices adequados ou com índices que não cobrem todas as combinações de colunas nas cláusulas OR, o planejador pode ser forçado a realizar varreduras sequenciais completas nas tabelas lineitem e part para cada parte da condição OR. Mesmo com Bitmap Index Scans (pág. 576.0), a necessidade de realizar Bitmap Heap Scans subsequentes para buscar as linhas da tabela (pág. 568.0) pode ser cara se muitas páginas de disco precisarem ser acessadas de forma não sequencial (alto random_page_cost, pág. 710.0). 2. CONSULTA OTIMIZADA
SELECT SUM(revenue) AS revenue
FROM (
SELECT
l.l_extendedprice _ (1 - l.l_discount) AS revenue
FROM
lineitem l
JOIN
part p ON p.p_partkey = l.l_partkey
WHERE
p.p_brand = 'Brand#12'
AND p.p_container IN ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG')
AND l.l_quantity BETWEEN 1 AND 11
AND p.p_size BETWEEN 1 AND 5
AND l.l_shipmode IN ('AIR', 'AIR REG')
AND l.l_shipinstruct = 'DELIVER IN PERSON'
UNION ALL
SELECT
l.l_extendedprice _ (1 - l.l_discount) AS revenue
FROM
lineitem l
JOIN
part p ON p.p_partkey = l.l_partkey
WHERE
p.p_brand = 'Brand#23'
AND p.p_container IN ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
AND l.l_quantity BETWEEN 10 AND 20
AND p.p_size BETWEEN 1 AND 10
AND l.l_shipmode IN ('AIR', 'AIR REG')
AND l.l_shipinstruct = 'DELIVER IN PERSON'
UNION ALL
SELECT
l.l_extendedprice \* (1 - l.l_discount) AS revenue
FROM
lineitem l
JOIN
part p ON p.p_partkey = l.l_partkey
WHERE
p.p_brand = 'Brand#34'
AND p.p_container IN ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
AND l.l_quantity BETWEEN 20 AND 30
AND p.p_size BETWEEN 1 AND 15
AND l.l_shipmode IN ('AIR', 'AIR REG')
AND l.l_shipinstruct = 'DELIVER IN PERSON'
) AS subquery_revenue; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
Mudanças Feitas: A principal mudança foi a refatoração da complexa cláusula OR em uma estrutura UNION ALL de subconsultas. Cada um dos três blocos OR originais foi transformado em uma subconsulta independente. As condições de junção (p.p_partkey = l.l_partkey) e os filtros comuns (l.l_shipmode IN ('AIR', 'AIR REG') e l.l_shipinstruct = 'DELIVER IN PERSON') foram repetidos em cada subconsulta. Os limites das cláusulas BETWEEN para l_quantity foram explicitamente calculados (ex: 1 + 10 se tornou 11).

Como o PostgreSQL Provavelmente Processará a Nova Consulta:

Otimização Independente das Subconsultas: O PostgreSQL otimizará cada uma das três subconsultas de forma independente. Isso permite que o planejador escolha o plano de execução mais eficiente para cada conjunto de condições AND, o que é uma vantagem significativa sobre a tentativa de otimizar uma única e complexa condição OR que abrange múltiplas tabelas e colunas.
Junção e Filtragem por Subconsulta: Para cada subconsulta, o planejador provavelmente executará uma junção entre lineitem e part (possivelmente um Nested Loop Join ou Hash Join, dependendo da seletividade dos filtros e das estatísticas). Os filtros específicos de cada subconsulta serão aplicados durante a varredura das tabelas.
Uso de Índices (Recomendação e Impacto Previsto): Para maximizar a performance, os seguintes índices são recomendados:
Para a tabela part:
CREATE INDEX idx_part_brand_container_size_partkey ON public.part (p_brand, p_container, p_size, p_partkey);
Este índice composto permitirá ao planejador realizar um Index Scan ou Bitmap Index Scan eficiente para filtrar as linhas da tabela part com base nas condições de igualdade (p_brand), IN (p_container) e BETWEEN (p_size). A inclusão de p_partkey no índice facilitará a junção com lineitem.
Para a tabela lineitem:
CREATE INDEX idx_lineitem_ship_qty_partkey_covering ON public.lineitem (l_shipinstruct, l_shipmode, l_quantity, l_partkey) INCLUDE (l_extendedprice, l_discount);
Este índice cobridor (covering index) permitirá um Index-Only Scan para as colunas l_shipinstruct, l_shipmode, l_quantity e l_partkey, além de incluir l_extendedprice e l_discount. Isso significa que o PostgreSQL poderá obter todos os dados necessários para os filtros, a junção e o cálculo da revenue diretamente do índice, sem precisar acessar as páginas da tabela (Heap Scan), o que reduz drasticamente o custo de I/O (pág. 568.0).
Combinação UNION ALL: Os resultados de cada subconsulta serão combinados usando UNION ALL. Esta operação é eficiente porque simplesmente concatena os resultados, sem a necessidade de ordenação ou remoção de duplicatas, que seriam operações mais custosas.
Agregação Final: Finalmente, a função SUM() será aplicada sobre todos os resultados combinados para calcular a receita total.
Impacto Previsto: A reescrita para UNION ALL, combinada com os índices sugeridos, deve transformar um plano de execução potencialmente lento (com Seq Scan ou Bitmap Heap Scan caros devido à complexidade do OR) em um conjunto de planos mais simples e diretos para cada subconsulta. Isso permitirá um uso muito mais eficaz dos índices, resultando em Index Scans ou Index-Only Scans que reduzem significativamente o número de blocos de disco lidos aleatoriamente (diminuindo o random_page_cost em relação ao seq_page_cost, conforme pág. 710.0) e o tempo de CPU gasto. O resultado esperado é uma melhoria substancial na performance da consulta.

Recomendações de Manutenção:

ANALYZE: Após a criação dos índices, é fundamental executar ANALYZE public.lineitem; e ANALYZE public.part; para atualizar as estatísticas do planejador de consultas. Estatísticas precisas são cruciais para que o PostgreSQL possa estimar corretamente a seletividade dos filtros e escolher o plano de execução mais eficiente.
VACUUM (ou AUTOVACUUM): Garanta que o autovacuum esteja configurado e funcionando corretamente nas tabelas lineitem e part. O VACUUM remove tuplas mortas e libera espaço, o que é importante para manter a eficiência dos índices e das tabelas, especialmente em ambientes com muitas operações de UPDATE ou DELETE.

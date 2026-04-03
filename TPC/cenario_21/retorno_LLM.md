# Consulta Otimizada

```sql
WITH orders_with_multiple_suppliers AS (
    SELECT
        l_orderkey
    FROM
        lineitem
    GROUP BY
        l_orderkey
    HAVING
        COUNT(DISTINCT l_suppkey) > 1
),
orders_suppliers_with_late_others AS (
    SELECT DISTINCT
        l1.l_orderkey,
        l1.l_suppkey
    FROM
        lineitem l1
    JOIN
        lineitem l3 ON l1.l_orderkey = l3.l_orderkey
    WHERE
        l1.l_suppkey <> l3.l_suppkey
        AND l3.l_receiptdate > l3.l_commitdate
)
SELECT
    s.s_name,
    COUNT(*) AS numwait
FROM
    nation n
JOIN
    supplier s ON s.s_nationkey = n.n_nationkey
JOIN
    lineitem l1 ON s.s_suppkey = l1.l_suppkey
JOIN
    orders o ON l1.l_orderkey = o.o_orderkey
LEFT JOIN
    orders_suppliers_with_late_others oslo ON l1.l_orderkey = oslo.l_orderkey AND l1.l_suppkey = oslo.l_suppkey
WHERE
    n.n_name = 'SAUDI ARABIA'
    AND o.o_orderstatus = 'F'
    AND l1.l_receiptdate > l1.l_commitdate
    AND l1.l_orderkey IN (SELECT l_orderkey FROM orders_with_multiple_suppliers)
    AND oslo.l_orderkey IS NULL
GROUP BY
    s.s_name
ORDER BY
    numwait DESC,
    s.s_name
LIMIT 100;
```

# Insights e Análises

1. ANÁLISE DE PROBLEMAS
   A consulta original apresenta vários gargalos de performance, principalmente devido à sua estrutura e à provável falta de índices otimizados:

Subqueries Correlacionadas Ineficientes: A consulta utiliza duas subqueries correlacionadas (EXISTS e NOT EXISTS) na cláusula WHERE. Para cada linha processada da tabela lineitem l1 na consulta principal, o PostgreSQL precisa reavaliar essas subqueries. Isso pode levar a um número massivo de execuções de subqueries, resultando em um desempenho exponencialmente lento. O otimizador pode ter dificuldade em transformar essas subqueries correlacionadas em joins eficientes, levando a planos de execução subótimos com varreduras repetidas.

Falta de Índices Adequados: As condições de filtro e join na cláusula WHERE e nas subqueries não são otimizadas por índices.

o_orderstatus = 'F': Requer um índice na coluna o_orderstatus da tabela orders.
l1.l_receiptdate > l1.l_commitdate: Esta é uma condição de intervalo em duas colunas. Sem um índice composto adequado, pode resultar em varreduras sequenciais (Seq Scan) ou Bitmap Scans menos eficientes.
n_name = 'SAUDI ARABIA': Requer um índice na coluna n_name da tabela nation.
As condições de join (s_suppkey = l1.l_suppkey, o_orderkey = l1.l_orderkey, s_nationkey = n_nationkey) e as condições das subqueries (l2.l_orderkey = l1.l_orderkey, l2.l_suppkey <> l1.l_suppkey, etc.) se beneficiariam de índices compostos ou múltiplos índices nas colunas envolvidas. Conforme o manual do PostgreSQL (pág. 497.0, Trecho 11), índices são usados para encontrar linhas que correspondem a uma condição. A ausência de índices força o planejador a recorrer a varreduras sequenciais ou Bitmap Scans mais caros, que envolvem mais I/O de disco (Manual pág. 569.0, Trecho 15).
Custo de Ordenação e Agregação: A consulta inclui GROUP BY s_name e ORDER BY numwait DESC, s_name LIMIT 100.

O GROUP BY requer uma operação de agregação (HashAggregate ou GroupAggregate), que pode ser intensiva em CPU e memória para grandes conjuntos de dados.
O ORDER BY final, especialmente com um agregado (numwait), exige uma etapa de ordenação explícita após a agregação. Embora o LIMIT 100 seja uma otimização importante, permitindo que o planejador pare de processar após encontrar os N primeiros resultados (Manual pág. 497.0, Trecho 1), a ordenação ainda precisa ser realizada sobre o resultado da agregação. Se a agregação produzir muitos grupos, a ordenação pode ser custosa (Manual pág. 569.0, Trecho 3). 2. CONSULTA OTIMIZADA
WITH orders_with_multiple_suppliers AS (
SELECT
l_orderkey
FROM
lineitem
GROUP BY
l_orderkey
HAVING
COUNT(DISTINCT l_suppkey) > 1
),
orders_suppliers_with_late_others AS (
SELECT DISTINCT
l1.l_orderkey,
l1.l_suppkey
FROM
lineitem l1
JOIN
lineitem l3 ON l1.l_orderkey = l3.l_orderkey
WHERE
l1.l_suppkey <> l3.l_suppkey
AND l3.l_receiptdate > l3.l_commitdate
)
SELECT
s.s_name,
COUNT(\*) AS numwait
FROM
nation n
JOIN
supplier s ON s.s_nationkey = n.n_nationkey
JOIN
lineitem l1 ON s.s_suppkey = l1.l_suppkey
JOIN
orders o ON l1.l_orderkey = o.o_orderkey
LEFT JOIN
orders_suppliers_with_late_others oslo ON l1.l_orderkey = oslo.l_orderkey AND l1.l_suppkey = oslo.l_suppkey
WHERE
n.n_name = 'SAUDI ARABIA'
AND o.o_orderstatus = 'F'
AND l1.l_receiptdate > l1.l_commitdate
AND l1.l_orderkey IN (SELECT l_orderkey FROM orders_with_multiple_suppliers)
AND oslo.l_orderkey IS NULL
GROUP BY
s.s_name
ORDER BY
numwait DESC,
s.s_name
LIMIT 100; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
Explicação das Mudanças:

Eliminação de Subqueries Correlacionadas: As subqueries EXISTS e NOT EXISTS foram transformadas em Common Table Expressions (CTEs) e, posteriormente, em joins/anti-joins.

A CTE orders_with_multiple_suppliers pré-calcula todos os l_orderkey que possuem mais de um fornecedor distinto. Isso substitui a subquery EXISTS original, que era correlacionada. O PostgreSQL pode materializar esta CTE uma vez e usá-la como uma tabela temporária ou otimizá-la como um Semi-Join.
A CTE orders_suppliers_with_late_others identifica pares (l_orderkey, l_suppkey) para os quais a condição NOT EXISTS original seria falsa (ou seja, existe outro fornecedor com data de recebimento tardia para o mesmo pedido). A condição NOT EXISTS é então implementada com um LEFT JOIN para esta CTE e uma verificação oslo.l_orderkey IS NULL. Esta é uma técnica comum e geralmente mais eficiente para converter NOT EXISTS em um Anti-Join, pois permite ao planejador usar estratégias de join otimizadas.
Impacto: Reduz drasticamente o número de execuções de subqueries, transformando-as em operações de join ou varreduras de CTEs materializadas, que o planejador pode otimizar de forma mais eficaz, evitando a reavaliação para cada linha da tabela externa.
Ordem das Operações e Filtros: A consulta foi reestruturada para iniciar com filtros mais seletivos e joins.

Começa filtrando nation por n_name = 'SAUDI ARABIA', que é uma condição altamente seletiva e reduz o conjunto de dados inicial.
Em seguida, junta-se com supplier, lineitem e orders, aplicando os filtros o_orderstatus = 'F' e l1.l_receiptdate > l1.l_commitdate o mais cedo possível.
As condições das CTEs são aplicadas posteriormente, usando IN para orders_with_multiple_suppliers e LEFT JOIN ... IS NULL para orders_suppliers_with_late_others.
Impacto: Reduz o tamanho dos conjuntos de dados intermediários que precisam ser processados nas etapas subsequentes, minimizando o trabalho de I/O e CPU.
Agregação e Ordenação: A lógica de GROUP BY e ORDER BY permanece a mesma, mas operará sobre um conjunto de dados já filtrado e processado pelas CTEs e joins.

Impacto: Embora a agregação e ordenação ainda sejam necessárias, elas serão aplicadas a um conjunto de dados significativamente menor e mais relevante, resultando em um processamento mais rápido. O LIMIT 100 continuará a ser uma otimização importante, permitindo que o planejador pare de processar após encontrar os 100 primeiros resultados ordenados (Manual pág. 497.0, Trecho 1).
Plano de Execução Estimado (com índices recomendados):

nation (n_name = 'SAUDI ARABIA'):

O planejador provavelmente executará um Index Scan na tabela nation usando idx_nation_name para encontrar a linha correspondente a 'SAUDI ARABIA'. Esta operação será muito rápida, retornando uma única linha.
supplier (s_nationkey):

Um Index Scan em idx_supplier_nationkey será usado para encontrar os fornecedores associados à n_nationkey da Arábia Saudita.
orders (o_orderstatus = 'F', o_orderkey):

Um Index Scan em idx_orders_orderstatus será usado para filtrar pedidos com o_orderstatus = 'F'. Este resultado será então unido à lineitem usando idx_orders_orderkey.
lineitem (l1.l_suppkey, l1.l_orderkey, l1.l_receiptdate > l1.l_commitdate):

A junção com supplier e orders, juntamente com o filtro l1.l_receiptdate > l1.l_commitdate, será otimizada por um Index Scan no índice composto idx_lineitem_composite. Este índice permitirá que o planejador acesse diretamente as linhas de lineitem que satisfazem todas as condições de join e filtro de data.
CTE orders_with_multiple_suppliers:

O planejador fará um Index Scan na tabela lineitem usando idx_lineitem_orderkey_suppkey (ou idx_lineitem_composite).
Em seguida, um HashAggregate ou GroupAggregate será executado para contar fornecedores distintos por l_orderkey.
O resultado desta CTE será materializado ou usado em um Hash Semi Join com a consulta principal para aplicar a condição IN.
CTE orders_suppliers_with_late_others:

Serão realizados Index Scans em idx_lineitem_composite (ou idx_lineitem_orderkey_suppkey_receiptdate_commitdate) para ambas as instâncias de lineitem (l1 e l3).
Um Hash Join será executado para l1.l_orderkey = l3.l_orderkey, aplicando os filtros l1.l_suppkey <> l3.l_suppkey e l3.l_receiptdate > l3.l_commitdate.
Um HashAggregate será usado para a operação DISTINCT nos pares (l_orderkey, l_suppkey).
O resultado desta CTE será materializado e usado em um Hash Anti Join com a consulta principal para aplicar a condição LEFT JOIN ... IS NULL.
Junção Final e Filtros:

Os resultados filtrados e unidos de nation, supplier, orders e lineitem serão processados.
Um Hash Semi Join será executado com os resultados da CTE orders_with_multiple_suppliers (para a condição IN).
Um Hash Anti Join será executado com os resultados da CTE orders_suppliers_with_late_others (para a condição LEFT JOIN ... IS NULL).
Agregação e Ordenação Final:

Um HashAggregate será realizado para o GROUP BY s_name e a função COUNT(\*).
Uma etapa de Sort será executada para ordenar os resultados agregados por numwait DESC, s_name.
Finalmente, a operação Limit selecionará os 100 primeiros resultados.
Recomendações de Índices:

Para maximizar o desempenho da consulta otimizada, os seguintes índices são recomendados:

Para a tabela nation:

CREATE INDEX idx_nation_name ON nation (n_name);
(Para a condição n_name = 'SAUDI ARABIA')

Para a tabela supplier:

CREATE INDEX idx_supplier_nationkey ON supplier (s_nationkey);
(Para o join com nation)

CREATE INDEX idx_supplier_suppkey ON supplier (s_suppkey);
(Para o join com lineitem. Assumindo que s_suppkey não é a chave primária ou não tem um índice implícito.)

Para a tabela orders:

CREATE INDEX idx_orders_orderstatus ON orders (o_orderstatus);
(Para a condição o_orderstatus = 'F')

CREATE INDEX idx_orders_orderkey ON orders (o_orderkey);
(Para o join com lineitem. Assumindo que o_orderkey não é a chave primária ou não tem um índice implícito.)

Para a tabela lineitem (o mais crítico): Um índice composto que cubra as colunas usadas em joins, filtros e nas CTEs será altamente benéfico.

CREATE INDEX idx_lineitem_composite ON lineitem (l_orderkey, l_suppkey, l_receiptdate, l_commitdate);
Este índice pode ser usado para:

Joins: l1.l_orderkey = o.o_orderkey, l1.l_suppkey = s.s_suppkey.
Filtro: l1.l_receiptdate > l1.l_commitdate.
CTE orders_with_multiple_suppliers: l_orderkey, l_suppkey para GROUP BY e COUNT(DISTINCT).
CTE orders_suppliers_with_late_others: l_orderkey, l_suppkey, l_receiptdate, l_commitdate para joins e filtros internos. A ordem das colunas no índice é importante para a seletividade e para cobrir as condições de forma eficiente (Manual pág. 496.0, Trecho 2). l_orderkey e l_suppkey são frequentemente usados em igualdades, enquanto l_receiptdate e l_commitdate são usados em comparações de intervalo.
Recomendações de Manutenção:

VACUUM ANALYZE;: Execute regularmente em todas as tabelas envolvidas (supplier, lineitem, orders, nation). Isso garante que as estatísticas do planejador estejam atualizadas, permitindo que o otimizador escolha o plano de execução mais eficiente para a consulta, especialmente com CTEs e joins complexos.
REINDEX: Se os índices ficarem muito fragmentados após muitas operações de INSERT/UPDATE/DELETE, considere recriá-los para melhorar o desempenho.
Monitoramento: Monitore o plano de execução da consulta otimizada com EXPLAIN ANALYZE em um ambiente de teste com dados representativos para validar as melhorias e ajustar os índices, se necessário.

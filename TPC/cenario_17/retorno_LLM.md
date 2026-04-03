# Consulta Otimizada

```sql
WITH PartAvgQuantity AS (
    SELECT
        l_partkey,
        0.2 * AVG(l_quantity) AS avg_qty_threshold
    FROM
        lineitem
    GROUP BY
        l_partkey
)
SELECT
    SUM(li.l_extendedprice) / 7.0 AS avg_yearly
FROM
    lineitem li
JOIN
    part p ON p.p_partkey = li.l_partkey
JOIN
    PartAvgQuantity paq ON li.l_partkey = paq.l_partkey
WHERE
    p.p_brand = 'Brand#23'
    AND p.p_container = 'MED BOX'
    AND li.l_quantity < paq.avg_qty_threshold;
```

# Insights e Análises

Aqui está a análise e otimização da consulta fornecida:

1. ANÁLISE DE PROBLEMAS
   A consulta original apresenta um gargalo de performance significativo devido principalmente ao uso de uma subconsulta correlacionada no predicado WHERE.

Subconsulta Correlacionada Ineficiente: A condição l_quantity < (SELECT 0.2 _ avg(l_quantity) FROM lineitem WHERE l_partkey = p_partkey) é uma subconsulta correlacionada. Isso significa que, para cada linha processada pela consulta externa, a subconsulta é executada novamente. Se a consulta externa processar N linhas e a subconsulta precisar escanear M linhas para cada execução, o custo total pode ser proporcional a N _ M, o que é extremamente ineficiente para tabelas grandes. O manual do PostgreSQL menciona que subplanos (que surgem de sub-SELECTs) podem ser transformados em planos de junção, mas quando não podem, resultam em planos como os que mostram a execução de subplanos, indicando um custo elevado (Conforme o manual do PostgreSQL (pág. 573)).

Ausência de Índices para Filtros e Junções: As condições p_brand = 'Brand#23', p_container = 'MED BOX' e a condição de junção p_partkey = l_partkey são SARGable, ou seja, podem se beneficiar diretamente de índices. Sem índices adequados nas colunas p_brand, p_container na tabela part e l_partkey na tabela lineitem, o otimizador de consultas provavelmente recorrerá a varreduras sequenciais (Seq Scan) nas tabelas, que são operações de I/O de disco muito mais caras do que varreduras de índice (Index Scan) para grandes volumes de dados (Conforme o manual do PostgreSQL (pág. 573, 710)). O custo relativo de varreduras sequenciais versus varreduras de índice é influenciado pelos parâmetros seq_page_cost e random_page_cost (Conforme o manual do PostgreSQL (pág. 710)).

Junção Implícita: Embora o PostgreSQL seja capaz de otimizar junções implícitas (separadas por vírgula no FROM), a sintaxe explícita JOIN é geralmente preferível para clareza e manutenção do código.

2. CONSULTA OTIMIZADA
   WITH PartAvgQuantity AS (
   SELECT
   l_partkey,
   0.2 \* AVG(l_quantity) AS avg_qty_threshold
   FROM
   lineitem
   GROUP BY
   l_partkey
   )
   SELECT
   SUM(li.l_extendedprice) / 7.0 AS avg_yearly
   FROM
   lineitem li
   JOIN
   part p ON p.p_partkey = li.l_partkey
   JOIN
   PartAvgQuantity paq ON li.l_partkey = paq.l_partkey
   WHERE
   p.p_brand = 'Brand#23'
   AND p.p_container = 'MED BOX'
   AND li.l_quantity < paq.avg_qty_threshold;
3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
   As mudanças na consulta visam eliminar a subconsulta correlacionada e otimizar as operações de junção e filtragem.

Mudanças Realizadas:

Descorrelação da Subconsulta: A subconsulta correlacionada foi transformada em uma Common Table Expression (CTE) chamada PartAvgQuantity. Esta CTE calcula 0.2 _ AVG(l_quantity) para cada l_partkey uma única vez e armazena o resultado. Em seguida, a CTE é unida à consulta principal usando li.l_partkey = paq.l_partkey. Isso transforma uma operação N _ M em uma operação de agregação (GROUP BY) seguida por uma junção, que é significativamente mais eficiente.
Junção Explícita: A junção entre lineitem e part foi reescrita usando a sintaxe JOIN explícita, melhorando a legibilidade e a clareza do código.
Plano de Execução Estimado (Comparativo):

Consulta Original:

O PostgreSQL provavelmente iniciaria com uma varredura sequencial (Seq Scan) ou uma varredura de índice (Index Scan) na tabela part para aplicar os filtros p_brand e p_container.
Em seguida, realizaria uma junção (provavelmente Nested Loop) com a tabela lineitem usando p_partkey = l_partkey.
Para cada linha resultante dessa junção, o otimizador executaria a subconsulta correlacionada. Essa subconsulta, por sua vez, faria uma varredura (provavelmente Seq Scan) na tabela lineitem para o l_partkey correspondente, calculando a média. Este padrão de "SubPlan" é explicitamente mencionado no manual como um cenário que pode ser caro (Conforme o manual do PostgreSQL (pág. 573)). O custo seria proibitivo para grandes conjuntos de dados.
Consulta Otimizada:

Execução da CTE PartAvgQuantity:
O PostgreSQL executará a CTE primeiro. Para SELECT l_partkey, 0.2 \* AVG(l_quantity) FROM lineitem GROUP BY l_partkey, um índice em lineitem(l_partkey, l_quantity) seria altamente benéfico. Com esse índice, o planner poderia usar um Index Scan ou Index Only Scan para ler os dados pré-ordenados por l_partkey e calcular a média de l_quantity de forma eficiente, seguido por uma agregação (GroupAggregate ou HashAggregate). Isso evita uma varredura sequencial completa da tabela lineitem para a agregação.
Junções e Filtros da Consulta Principal:
O otimizador começaria filtrando a tabela part usando p.p_brand = 'Brand#23' e p.p_container = 'MED BOX'. Com o índice recomendado, ele usaria um Index Scan ou Bitmap Index Scan para localizar rapidamente as linhas correspondentes (Conforme o manual do PostgreSQL (pág. 568)).
As linhas filtradas de part seriam então unidas à tabela lineitem em p.p_partkey = li.l_partkey. Um índice em lineitem(l_partkey) facilitaria essa junção (por exemplo, Hash Join ou Merge Join se os dados estiverem pré-ordenados, ou Nested Loop com Index Scan em lineitem).
Finalmente, o resultado seria unido à CTE PartAvgQuantity em li.l_partkey = paq.l_partkey. O índice em lineitem(l_partkey) e a estrutura da CTE (que já tem l_partkey como chave) otimizariam essa junção.
A condição li.l_quantity < paq.avg_qty_threshold seria aplicada como um filtro final. O índice em lineitem(l_partkey, l_quantity) também ajudaria a otimizar o acesso a l_quantity durante a varredura da tabela lineitem para a junção e filtragem.
Impacto Previsto:

A principal melhoria será a redução drástica do número de execuções da operação de agregação. Em vez de N execuções da subconsulta, teremos uma única execução da CTE, seguida por junções eficientes. Isso transformará um plano de execução potencialmente exponencial em um plano linear ou logarítmico, dependendo do tamanho dos dados e da eficácia dos índices. A preferência por Index Scan em vez de Seq Scan para as condições de filtro e junção reduzirá significativamente o custo de I/O de disco (Conforme o manual do PostgreSQL (pág. 710)).

Recomendações de Índices:

Para maximizar a performance da consulta otimizada, os seguintes índices são recomendados:

Na tabela part:

CREATE INDEX idx_part_brand_container_partkey ON public.part (p_brand, p_container, p_partkey);
Este índice composto cobrirá as condições de filtro (p_brand, p_container) e a coluna de junção (p_partkey), permitindo que o PostgreSQL use um Index Scan eficiente para localizar as linhas relevantes na tabela part. (Conforme o manual do PostgreSQL (pág. 493, 497)).

Na tabela lineitem:

CREATE INDEX idx_lineitem_partkey_quantity ON public.lineitem (l_partkey, l_quantity);
Este índice composto é crucial para a performance da CTE PartAvgQuantity (para GROUP BY l_partkey e AVG(l_quantity)) e para a junção com a tabela part e a CTE, bem como para a condição de filtro final li.l_quantity < paq.avg_qty_threshold. Ele permitirá que o PostgreSQL acesse l_partkey e l_quantity de forma eficiente.

Recomendações de Manutenção:

VACUUM ANALYZE: É fundamental executar VACUUM ANALYZE regularmente nas tabelas lineitem e part. O comando ANALYZE coleta estatísticas de distribuição de dados, que são vitais para o otimizador de consultas escolher o plano de execução mais eficiente, incluindo o uso de índices. VACUUM ajuda a recuperar espaço e a evitar o problema de "wraparound" de IDs de transação.
Monitoramento: Monitore o plano de execução da nova consulta usando EXPLAIN ANALYZE para confirmar que os índices estão sendo utilizados conforme o esperado e para identificar quaisquer outros gargalos.

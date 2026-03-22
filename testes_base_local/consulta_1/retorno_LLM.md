# Consulta Otimizada

```sql
SELECT DISTINCT
    o_orderkey,
    o_orderdate,
    l_extendedprice
FROM (
    SELECT
        o.o_orderkey,
        o.o_orderdate,
        l.l_extendedprice
    FROM
        public.orders o
    JOIN
        public.lineitem l ON o.o_orderkey = l.l_orderkey
    WHERE
        o.o_orderstatus = 'F'

    UNION ALL

    SELECT
        o.o_orderkey,
        o.o_orderdate,
        l.l_extendedprice
    FROM
        public.orders o
    JOIN
        public.lineitem l ON o.o_orderkey = l.l_orderkey
    WHERE
        l.l_quantity > 40
) AS combined_results;
```

# Insights e Análises

ANÁLISE DE PROBLEMAS
A consulta original apresenta um gargalo de performance significativo devido à condição OR que abrange colunas de tabelas diferentes (o.o_orderstatus da tabela public.orders e l.l_quantity da tabela public.lineitem).

Dificuldade de Otimização Direta do OR entre Tabelas: Conforme o Trecho 3 (Manual pág. 497.0), "a query like WHERE a = 5 OR b = 6 could not directly use the index" quando as condições são em colunas diferentes de uma única tabela para um único Index Scan. Embora o PostgreSQL tenha a capacidade de combinar múltiplos índices para condições OR na mesma tabela usando BitmapOr (conforme Trechos 12 e 14, Manual pág. 497.0-498.0), essa funcionalidade não se estende diretamente e de forma eficiente para condições OR que envolvem colunas de tabelas diferentes que estão sendo unidas. O otimizador de consultas teria dificuldade em aplicar eficientemente índices para ambas as partes do OR antes ou durante a operação de JOIN. Isso pode levar a um processamento ineficiente do JOIN em um conjunto de dados maior antes que o filtro OR possa ser aplicado.

Potencial para Seq Scan e Hash Join em Grande Volume de Dados: Sem índices adequados nas colunas o_orderstatus e l_quantity, e devido à complexidade do OR entre tabelas, o planejador pode recorrer a um Seq Scan (varredura sequencial) em uma ou ambas as tabelas (public.orders e public.lineitem). Um Seq Scan é ineficiente para tabelas grandes quando apenas uma pequena fração das linhas é relevante, resultando em alto custo de I/O de disco (conforme seq_page_cost no Trecho 18, Manual pág. 710.0). O JOIN subsequente (provavelmente um Hash Join ou Nested Loop Join) teria que processar um volume muito maior de dados intermediários antes que a condição OR pudesse ser aplicada, aumentando significativamente o tempo de execução.

Falta de SARGability para o OR combinado: Embora o.o_orderstatus = 'F' e l.l_quantity > 40 sejam individualmente SARGable (ou seja, podem se beneficiar de índices), a combinação OR entre eles, especialmente em tabelas diferentes, impede que um único índice composto seja utilizado de forma eficaz para filtrar os dados antes do JOIN. A ausência de índices nas colunas o_orderstatus, l_quantity, o_orderkey e l_orderkey agravaria ainda mais o problema, forçando varreduras completas e joins caros.

CONSULTA OTIMIZADA
SELECT DISTINCT
o_orderkey,
o_orderdate,
l_extendedprice
FROM (
SELECT
o.o_orderkey,
o.o_orderdate,
l.l_extendedprice
FROM
public.orders o
JOIN
public.lineitem l ON o.o_orderkey = l.l_orderkey
WHERE
o.o_orderstatus = 'F'

    UNION ALL

    SELECT
        o.o_orderkey,
        o.o_orderdate,
        l.l_extendedprice
    FROM
        public.orders o
    JOIN
        public.lineitem l ON o.o_orderkey = l.l_orderkey
    WHERE
        l.l_quantity > 40

) AS combined_results;
EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
Mudanças Feitas: A consulta foi reescrita utilizando a cláusula UNION ALL para dividir a condição OR original em duas subconsultas independentes. Cada subconsulta agora contém uma das condições do OR original (o.o_orderstatus = 'F' ou l.l_quantity > 40). Um SELECT DISTINCT foi adicionado à consulta externa para garantir que a semântica original seja mantida, eliminando quaisquer linhas duplicadas que possam surgir se um par (o, l) satisfizer ambas as condições do OR.

Processamento e Impacto Previsto:

Otimização de Subconsultas Independentes: Ao separar as condições com UNION ALL, o planejador do PostgreSQL pode otimizar cada subconsulta de forma independente. Isso permite o uso eficiente de índices para cada condição WHERE, o que não seria possível de forma tão direta com o OR entre tabelas.

Para a primeira subconsulta (WHERE o.o_orderstatus = 'F'): O PostgreSQL poderá utilizar um Index Scan ou Bitmap Heap Scan na coluna o_orderstatus da tabela public.orders. Isso reduzirá drasticamente o número de linhas de orders a serem processadas.
Para a segunda subconsulta (WHERE l.l_quantity > 40): O PostgreSQL poderá utilizar um Index Scan ou Bitmap Heap Scan na coluna l_quantity da tabela public.lineitem. Isso reduzirá drasticamente o número de linhas de lineitem a serem processadas.
Esta abordagem se alinha com a capacidade do PostgreSQL de usar múltiplos índices, mas de forma mais controlada e eficiente para condições OR complexas entre tabelas, evitando a necessidade de varreduras sequenciais completas (Trecho 17, Manual pág. 568.0).
Melhoria nos Joins: Com as linhas filtradas por índices em cada subconsulta, o volume de dados a ser unido é significativamente reduzido. O JOIN entre public.orders e public.lineitem (na condição o.o_orderkey = l.l_orderkey) será mais eficiente, possivelmente utilizando Merge Join ou Hash Join em conjuntos de dados menores, especialmente se houver índices nas chaves de join (o_orderkey e l_orderkey) (Trecho 4, Manual pág. 2399.0).

Combinação de Resultados (UNION ALL): Os resultados das duas subconsultas são combinados por UNION ALL. Este operador simplesmente anexa os resultados, o que é geralmente uma operação rápida, pois não envolve ordenação ou remoção de duplicatas nesta fase.

Remoção de Duplicatas (SELECT DISTINCT): A operação SELECT DISTINCT final será aplicada sobre o conjunto combinado de resultados. Isso provavelmente envolverá uma etapa de Sort e Unique ou HashAggregate para identificar e remover linhas duplicadas. Embora esta etapa adicione um custo (principalmente de CPU e memória para ordenação/hashing), ela é geralmente mais eficiente do que tentar otimizar um OR complexo entre tabelas diferentes com Seq Scans e Hash Joins em grandes volumes de dados.

Plano de Execução Estimado (Exemplo): O plano de execução provável para a consulta otimizada seria uma estrutura como:

HashAggregate (cost=... rows=... width=...) -- Para o SELECT DISTINCT
-> Append (cost=... rows=... width=...) -- Para o UNION ALL
-> Subquery 1 (cost=... rows=... width=...)
-> Hash Join (or Merge Join) (cost=... rows=... width=...)
-> Bitmap Heap Scan on orders o (cost=... rows=... width=...)
-> Bitmap Index Scan on idx_orders_orderstatus (cost=... rows=... width=0)
-> Index Scan (or Bitmap Heap Scan) on lineitem l (cost=... rows=... width=...)
-> Index Scan on idx_lineitem_orderkey (cost=... rows=... width=0)
-> Subquery 2 (cost=... rows=... width=...)
-> Hash Join (or Merge Join) (cost=... rows=... width=...)
-> Bitmap Heap Scan on lineitem l (cost=... rows=... width=...)
-> Bitmap Index Scan on idx_lineitem_quantity (cost=... rows=... width=0)
-> Index Scan (or Bitmap Heap Scan) on orders o (cost=... rows=... width=...)
-> Index Scan on idx_orders_orderkey (cost=... rows=... width=0)
Este plano representa uma mudança fundamental de Seq Scan para Index Scan ou Bitmap Heap Scan nas tabelas public.orders e public.lineitem para as condições de filtro, resultando em uma redução drástica no I/O de disco e no tempo de CPU, especialmente para tabelas grandes onde as condições WHERE são seletivas.

Recomendações de Índices: Para maximizar a performance da consulta otimizada, os seguintes índices são cruciais:

CREATE INDEX idx_orders_orderstatus ON public.orders (o_orderstatus);
Este índice permitirá que a primeira subconsulta filtre rapidamente as ordens com o_orderstatus = 'F', utilizando um Index Scan ou Bitmap Index Scan.
CREATE INDEX idx_lineitem_quantity ON public.lineitem (l_quantity);
Este índice permitirá que a segunda subconsulta filtre rapidamente os itens de linha com l_quantity > 40, utilizando um Index Scan ou Bitmap Index Scan.
CREATE INDEX idx_orders_orderkey ON public.orders (o_orderkey);
Essencial para otimizar a operação JOIN na tabela public.orders. Se o_orderkey já for uma chave primária, este índice já existirá.
CREATE INDEX idx_lineitem_orderkey ON public.lineitem (l_orderkey);
Essencial para otimizar a operação JOIN na tabela public.lineitem. Se l_orderkey for uma chave estrangeira, um índice pode já existir.
Recomendações de Manutenção:

ANALYZE: Após a criação dos índices e periodicamente, execute ANALYZE public.orders; e ANALYZE public.lineitem;. Isso garantirá que o planejador de consultas tenha estatísticas atualizadas sobre a distribuição dos dados e a seletividade dos índices, permitindo-lhe escolher o plano de execução mais eficiente.
VACUUM: Para tabelas com muitas operações de INSERT, UPDATE e DELETE, o VACUUM (ou autovacuum) é fundamental para remover tuplas mortas e manter a saúde do índice e da tabela, evitando o inchaço e garantindo que os índices permaneçam eficientes.

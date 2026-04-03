# Consulta Otimizada

```sql
WITH FilteredCustomers AS (
    SELECT
        c.c_custkey,
        substring(c.c_phone FROM 1 FOR 2) AS cntrycode,
        c.c_acctbal
    FROM
        customer c
    WHERE
        substring(c.c_phone FROM 1 FOR 2) IN ('13', '31', '23', '29', '30', '18', '17')
        AND c.c_acctbal > 0.00
),
AvgFilteredAcctBal AS (
    SELECT AVG(fc.c_acctbal) AS avg_bal
    FROM FilteredCustomers fc
)
SELECT
    fc.cntrycode,
    COUNT(fc.c_custkey) AS numcust,
    SUM(fc.c_acctbal) AS totacctbal
FROM
    FilteredCustomers fc
CROSS JOIN
    AvgFilteredAcctBal afab
LEFT JOIN
    orders o ON fc.c_custkey = o.o_custkey
WHERE
    fc.c_acctbal > afab.avg_bal
    AND o.o_orderkey IS NULL
GROUP BY
    fc.cntrycode
ORDER BY
    fc.cntrycode;
```

# Insights e Análises

Como especialista em banco de dados PostgreSQL, analisei a consulta original e preparei uma versão otimizada, juntamente com uma análise detalhada.

1. ANÁLISE DE PROBLEMAS:
   A consulta original apresenta várias ineficiências que podem levar a um desempenho lento, especialmente em tabelas grandes:

Subquery Correlacionada ou Re-executada para AVG(c_acctbal): A subconsulta que calcula AVG(c_acctbal) é aninhada dentro da cláusula WHERE da consulta principal. Embora o PostgreSQL possa otimizar subconsultas escalares para serem executadas apenas uma vez, a repetição da mesma lógica de filtragem (substring(c_phone from 1 for 2) in (...) e c_acctbal > 0.00) dentro da subconsulta e da consulta externa sugere que a tabela customer pode ser escaneada ou processada múltiplas vezes para as mesmas condições. Isso aumenta o custo de I/O e CPU. Conforme o manual do PostgreSQL, subplanos podem ser caros (pág. 573.0).
Função substring() não SARGable: A condição substring(c_phone from 1 for 2) in (...) é aplicada repetidamente. O uso da função substring() em uma cláusula WHERE impede que um índice comum na coluna c_phone seja utilizado eficientemente para essa condição. Isso força o planejador a realizar um Seq Scan (varredura sequencial) na tabela customer ou, no mínimo, a escanear um índice e aplicar a função em cada linha, o que é ineficiente para grandes volumes de dados. Para que uma condição seja SARGable, ela deve permitir que o planejador de consultas utilize um índice diretamente para localizar as linhas. O manual discute como as cláusulas de consulta podem usar colunas indexadas (pág. 493.0).
NOT EXISTS Ineficiente: A cláusula NOT EXISTS (SELECT \* FROM orders WHERE o_custkey = c_custkey) pode ser menos eficiente do que uma LEFT JOIN com uma condição WHERE o_orderkey IS NULL. Embora o PostgreSQL seja inteligente o suficiente para otimizar NOT EXISTS em alguns casos, a LEFT JOIN oferece ao planejador mais flexibilidade para escolher algoritmos de junção (como Hash Join ou Merge Join) que podem ser mais rápidos, especialmente se a coluna o_custkey não estiver indexada na tabela orders.
GROUP BY e ORDER BY em Expressão Calculada: As operações GROUP BY cntrycode e ORDER BY cntrycode dependem da expressão substring(c_phone from 1 for 2). Se essa expressão não for indexada, o PostgreSQL terá que calcular cntrycode para todas as linhas qualificadas e, em seguida, realizar uma etapa de ordenação explícita (Sort) para agrupar e ordenar os resultados. Isso pode ser custoso em termos de CPU e memória, especialmente se o conjunto de resultados intermediário for grande (pág. 497.0, 569.0). 2. CONSULTA OTIMIZADA:
WITH FilteredCustomers AS (
SELECT
c.c_custkey,
substring(c.c_phone FROM 1 FOR 2) AS cntrycode,
c.c_acctbal
FROM
customer c
WHERE
substring(c.c_phone FROM 1 FOR 2) IN ('13', '31', '23', '29', '30', '18', '17')
AND c.c_acctbal > 0.00
),
AvgFilteredAcctBal AS (
SELECT AVG(fc.c_acctbal) AS avg_bal
FROM FilteredCustomers fc
)
SELECT
fc.cntrycode,
COUNT(fc.c_custkey) AS numcust,
SUM(fc.c_acctbal) AS totacctbal
FROM
FilteredCustomers fc
CROSS JOIN
AvgFilteredAcctBal afab
LEFT JOIN
orders o ON fc.c_custkey = o.o_custkey
WHERE
fc.c_acctbal > afab.avg_bal
AND o.o_orderkey IS NULL
GROUP BY
fc.cntrycode
ORDER BY
fc.cntrycode; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO:
As mudanças foram projetadas para reduzir varreduras redundantes, otimizar condições de filtro e junções, e melhorar o desempenho de agrupamento e ordenação.

Uso de CTEs (Common Table Expressions):

A CTE FilteredCustomers pré-filtra a tabela customer uma única vez, aplicando as condições substring(c_phone FROM 1 FOR 2) IN (...) e c_acctbal > 0.00. Isso evita a reavaliação dessas condições e a varredura repetida da tabela customer.
A CTE AvgFilteredAcctBal calcula a média de c_acctbal apenas uma vez a partir do conjunto de dados já filtrado por FilteredCustomers. Isso elimina a subconsulta aninhada e a potencial varredura redundante da tabela customer para calcular a média. O resultado é uma única linha que é então combinada com FilteredCustomers usando um CROSS JOIN (que é eficiente para uma única linha).
Impacto Previsto: Redução significativa do custo de CPU e I/O, pois a tabela customer é processada de forma mais eficiente e as operações caras são realizadas uma vez.
Substituição de NOT EXISTS por LEFT JOIN / IS NULL:

A cláusula NOT EXISTS foi substituída por um LEFT JOIN entre FilteredCustomers e orders na coluna c_custkey (que corresponde a o_custkey). A condição o.o_orderkey IS NULL no WHERE filtra apenas os clientes que não possuem pedidos correspondentes.
Impacto Previsto: O planejador do PostgreSQL pode ter mais opções para otimizar a junção, como usar um Hash Join ou Merge Join se os índices apropriados estiverem disponíveis, o que geralmente é mais eficiente do que o Nested Loop que NOT EXISTS pode induzir em alguns cenários.
Otimização de GROUP BY e ORDER BY:

Ao pré-calcular cntrycode na CTE FilteredCustomers, o GROUP BY e ORDER BY operam em uma coluna já definida.
Impacto Previsto: Com os índices sugeridos abaixo, o PostgreSQL poderá usar um Index Scan para satisfazer as condições de filtro, agrupamento e ordenação, evitando uma etapa de Sort explícita, que é custosa para grandes conjuntos de dados (pág. 497.0, 569.0).
Plano de Execução Estimado (com índices):

Com os índices recomendados, o PostgreSQL provavelmente seguirá um plano de execução semelhante a este:

AvgFilteredAcctBal CTE:
Index Scan ou Bitmap Index Scan na tabela customer usando o índice funcional idx_customer_cntrycode_acctbal para encontrar linhas que satisfazem substring(c_phone FROM 1 FOR 2) IN (...) e c_acctbal > 0.00.
Aggregate para calcular AVG(c_acctbal).
FilteredCustomers CTE:
Index Scan ou Bitmap Index Scan na tabela customer usando o índice funcional idx_customer_cntrycode_acctbal para encontrar linhas que satisfazem substring(c_phone FROM 1 FOR 2) IN (...) e c_acctbal > 0.00.
As colunas c_custkey, cntrycode e c_acctbal seriam extraídas.
Junção e Filtragem Final:
Hash Join ou Merge Join entre FilteredCustomers e orders (usando idx_orders_custkey) para identificar clientes sem pedidos.
Filter para aplicar fc.c_acctbal > afab.avg_bal e o.o_orderkey IS NULL.
Group Aggregate para COUNT e SUM por cntrycode.
Index Scan (se o índice funcional for usado para cntrycode) ou Sort para a cláusula ORDER BY cntrycode.
Recomendações de Manutenção e Índices:

Para maximizar o desempenho da consulta otimizada, os seguintes índices são cruciais:

Índice Funcional na Tabela customer: Este índice é fundamental para tornar a condição substring(c_phone FROM 1 FOR 2) SARGable e para otimizar o GROUP BY e ORDER BY.

CREATE INDEX idx_customer_cntrycode_acctbal
ON public.customer (substring(c_phone FROM 1 FOR 2), c_acctbal)
WHERE c_acctbal > 0.00;
Explicação: Este é um índice composto funcional e parcial. Ele indexa a expressão substring(c_phone FROM 1 FOR 2) e a coluna c_acctbal. A cláusula WHERE c_acctbal > 0.00 reduz o tamanho do índice, pois a consulta original e a otimizada sempre filtram por essa condição. Isso permite que o planejador use o índice para as condições de filtro, agrupamento e ordenação, potencialmente resultando em um Index Only Scan se todas as colunas necessárias (c_custkey, cntrycode, c_acctbal) puderem ser obtidas do índice (se c_custkey for incluído ou se o índice for "cobridor").
Índice na Tabela orders: Este índice é essencial para a eficiência da LEFT JOIN.

CREATE INDEX idx_orders_custkey
ON public.orders (o_custkey);
Explicação: Um índice na coluna o_custkey da tabela orders permitirá que o PostgreSQL encontre rapidamente os pedidos de um cliente específico, otimizando a operação LEFT JOIN e a condição o.o_orderkey IS NULL.
Manutenção:

ANALYZE: Após a criação dos índices e sempre que houver mudanças significativas nos dados (inserções, atualizações, exclusões), execute ANALYZE customer; e ANALYZE orders;. Isso garante que o planejador de consultas tenha estatísticas atualizadas para tomar as melhores decisões de plano de execução.
VACUUM (ou AUTOVACUUM): Certifique-se de que o autovacuum esteja configurado e funcionando corretamente. VACUUM é crucial para remover tuplas mortas e manter o desempenho da tabela e dos índices, especialmente em tabelas com muitas operações de UPDATE ou DELETE.

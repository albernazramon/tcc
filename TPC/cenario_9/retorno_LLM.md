# Consulta Otimizada

```sql
SELECT
    n.n_name AS nation,
    EXTRACT(YEAR FROM o.o_orderdate) AS o_year,
    SUM(l.l_extendedprice * (1 - l.l_discount) - ps.ps_supplycost * l.l_quantity) AS sum_profit
FROM
    part AS p
JOIN
    lineitem AS l ON p.p_partkey = l.l_partkey
JOIN
    partsupp AS ps ON l.l_partkey = ps.ps_partkey AND l.l_suppkey = ps.ps_suppkey
JOIN
    supplier AS s ON l.l_suppkey = s.s_suppkey
JOIN
    orders AS o ON l.l_orderkey = o.o_orderkey
JOIN
    nation AS n ON s.s_nationkey = n.n_nationkey
WHERE
    p.p_name LIKE '%green%'
GROUP BY
    n.n_name,
    EXTRACT(YEAR FROM o.o_orderdate)
ORDER BY
    n.n_name,
    EXTRACT(YEAR FROM o.o_orderdate) DESC;
```

# Insights e Análises

1. ANÁLISE DE PROBLEMAS
   A consulta original apresenta vários gargalos de performance, principalmente devido à falta de índices adequados e à natureza de algumas operações:

Filtro p_name LIKE '%green%': Esta é a principal causa de lentidão. O uso do operador LIKE com um curinga (%) no início da string (%green%) impede que um índice B-tree padrão seja utilizado de forma eficiente. Conforme o manual do PostgreSQL (pág. 493), índices B-tree são eficazes para LIKE 'foo%' (ancorado à esquerda), mas não para padrões com curinga inicial. Isso força o planejador a realizar um Seq Scan (varredura sequencial) completo na tabela part, lendo todas as suas linhas para encontrar as correspondências. Para tabelas grandes, essa operação é extremamente custosa em termos de I/O de disco.

Múltiplas Junções (JOINs): A consulta envolve junções entre seis tabelas (part, supplier, lineitem, partsupp, orders, nation). Sem índices nas colunas de junção (chaves primárias e estrangeiras), o planejador pode recorrer a Hash Joins ou Nested Loop Joins ineficientes. Hash Joins podem consumir muita memória, e Nested Loop Joins são lentos se a tabela interna não tiver um índice na coluna de junção e a tabela externa for grande. O custo de acesso aleatório a páginas de disco (associado a Index Scans) versus acesso sequencial (associado a Seq Scans) é um fator que o planejador considera (Conforme o manual do PostgreSQL, pág. 710).

Agregação (GROUP BY) e Ordenação (ORDER BY): A consulta agrupa os resultados por nation e o_year e os ordena da mesma forma, com o_year em ordem decrescente.

A função EXTRACT(YEAR FROM o_orderdate) impede o uso direto de um índice B-tree simples na coluna o_orderdate para a parte do ano. Embora um índice de expressão pudesse ser criado, a combinação com n_name de outra tabela dificulta a otimização de GROUP BY/ORDER BY com um único índice composto.
Se o resultado intermediário das junções for grande, o GROUP BY provavelmente resultará em um Hash Aggregate, que pode ser intensivo em memória.
A cláusula ORDER BY exigirá um passo de Sort explícito se os dados não estiverem naturalmente ordenados pelas chaves de ordenação após as junções e a agregação (Conforme o manual do PostgreSQL, pág. 569, 497). Um Bitmap Index Scan, por exemplo, não garante a ordem dos resultados (Conforme o manual do PostgreSQL, pág. 498). 2. CONSULTA OTIMIZADA
SELECT
n.n_name AS nation,
EXTRACT(YEAR FROM o.o_orderdate) AS o_year,
SUM(l.l_extendedprice _ (1 - l.l_discount) - ps.ps_supplycost _ l.l_quantity) AS sum_profit
FROM
part AS p
JOIN
lineitem AS l ON p.p_partkey = l.l_partkey
JOIN
partsupp AS ps ON l.l_partkey = ps.ps_partkey AND l.l_suppkey = ps.ps_suppkey
JOIN
supplier AS s ON l.l_suppkey = s.s_suppkey
JOIN
orders AS o ON l.l_orderkey = o.o_orderkey
JOIN
nation AS n ON s.s_nationkey = n.n_nationkey
WHERE
p.p_name LIKE '%green%'
GROUP BY
n.n_name,
EXTRACT(YEAR FROM o.o_orderdate)
ORDER BY
n.n_name,
EXTRACT(YEAR FROM o.o_orderdate) DESC; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
A consulta SQL otimizada mantém a mesma lógica da original, mas a performance será drasticamente melhorada pela adição de índices estratégicos e pela forma como o planejador do PostgreSQL os utilizará.

Explicação das Mudanças:

A principal "mudança" não está na sintaxe SQL, mas na infraestrutura de índices que permitirá ao PostgreSQL executar a consulta de forma mais eficiente. A reescrita para INNER JOIN explícito é uma prática recomendada para clareza, mas não altera o plano de execução em comparação com a sintaxe implícita do FROM com WHERE.

Impacto Previsto e Plano de Execução Estimado:

Otimização do Filtro p_name LIKE '%green%':

Antes: Seq Scan na tabela part.
Depois: Com a criação da extensão pg_trgm e um índice GIN na coluna p_name, o PostgreSQL poderá usar um Bitmap Index Scan (ou Index Scan dependendo da seletividade) na tabela part. Isso transformará a varredura completa da tabela em uma busca indexada muito mais rápida, identificando as p_partkeys relevantes de forma eficiente (Conforme o manual do PostgreSQL, pág. 2973, 2975). O Bitmap Index Scan primeiro encontra as localizações das linhas no índice e depois as busca na tabela, o que é mais eficiente do que um Seq Scan quando poucas linhas são necessárias (Conforme o manual do PostgreSQL, pág. 8).
Otimização das Junções (JOINs):

Antes: Potenciais Hash Joins ou Nested Loop Joins ineficientes devido à falta de índices nas chaves de junção.
Depois: A criação de índices B-tree nas chaves primárias e estrangeiras das tabelas envolvidas permitirá ao planejador escolher planos de junção mais eficientes. Por exemplo, Nested Loop Joins se tornarão muito mais rápidos, pois o acesso à tabela interna será via Index Scan em vez de Seq Scan. Merge Joins também podem ser utilizados se os dados já estiverem ordenados pelas chaves de junção. O planejador considerará o custo de acesso aleatório versus sequencial ao escolher o tipo de junção (Conforme o manual do PostgreSQL, pág. 710).
Otimização de Agregação e Ordenação:

Antes: Provável Hash Aggregate seguido por um Sort explícito, que pode ser custoso para grandes conjuntos de resultados.
Depois:
Um índice de expressão em orders (EXTRACT(YEAR FROM o_orderdate)) ajudará o planejador a calcular o_year de forma mais eficiente e potencialmente a pré-filtrar ou pré-ordenar os dados de orders por ano.
Um índice em nation (n_name) ajudará a ordenar os nomes das nações.
Embora um único índice composto para (n_name, EXTRACT(YEAR FROM o_orderdate) DESC) não seja diretamente aplicável a uma única tabela para cobrir ambas as colunas de agrupamento/ordenação (pois vêm de tabelas diferentes), a otimização das junções e dos filtros iniciais reduzirá o volume de dados que precisam ser agregados e ordenados.
O plano de execução mais provável ainda envolverá um Hash Aggregate para o GROUP BY e um Sort final para o ORDER BY. No entanto, com os dados de entrada para essas operações sendo significativamente menores e mais rapidamente acessados, o custo total será muito menor. O planejador pode até considerar um Incremental Sort se a ordenação por n_name já estiver garantida (Conforme o manual do PostgreSQL, pág. 569).
Recomendações de Índices:

Assumindo que as chaves primárias já possuem índices B-tree únicos (criados automaticamente ou manualmente), as seguintes recomendações de índices são cruciais:

Para o filtro p_name LIKE '%green%':

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_part_p_name_trgm ON public.part USING GIN (p_name gin_trgm_ops);
Para otimizar as junções (chaves estrangeiras):

CREATE INDEX idx_lineitem_partkey ON public.lineitem (l_partkey);
CREATE INDEX idx_lineitem_suppkey ON public.lineitem (l_suppkey);
CREATE INDEX idx_lineitem_orderkey ON public.lineitem (l_orderkey);
CREATE INDEX idx_supplier_nationkey ON public.supplier (s_nationkey);
-- Para partsupp, se ps_partkey e ps_suppkey não forem já parte de uma PK composta indexada,
-- ou se a ordem da junção favorecer:
-- CREATE INDEX idx_partsupp_partkey_suppkey ON public.partsupp (ps_partkey, ps_suppkey);
-- CREATE INDEX idx_partsupp_suppkey_partkey ON public.partsupp (ps_suppkey, ps_partkey);
Para otimizar a extração do ano e auxiliar na ordenação:

CREATE INDEX idx_orders_o_orderdate_year ON public.orders (EXTRACT(YEAR FROM o_orderdate));
-- Para auxiliar na ordenação por n_name:
CREATE INDEX idx_nation_name ON public.nation (n_name);
Recomendações de Manutenção:

ANALYZE: Após a criação de novos índices e após qualquer alteração significativa nos dados (grandes inserções, atualizações, exclusões), é fundamental executar ANALYZE em todas as tabelas envolvidas (part, supplier, lineitem, partsupp, orders, nation). Isso garante que o planejador de consultas tenha estatísticas atualizadas sobre a distribuição dos dados e a seletividade dos índices, permitindo-lhe escolher os planos de execução mais eficientes (Conforme o manual do PostgreSQL, pág. 710, que descreve como o planejador estima custos).
VACUUM: A execução regular de VACUUM (ou autovacuum) é essencial para remover tuplas mortas, recuperar espaço em disco e evitar o inchaço das tabelas e índices. Isso mantém a performance das operações de leitura e escrita e a saúde geral do banco de dados.

# Consulta Otimizada

```sql
SELECT
    100.00 * SUM(CASE
        WHEN p.p_type LIKE 'PROMO%'
            THEN l.l_extendedprice * (1 - l.l_discount)
        ELSE 0
    END) / SUM(l.l_extendedprice * (1 - l.l_discount)) AS promo_revenue
FROM
    public.lineitem AS l
INNER JOIN
    public.part AS p ON l.l_partkey = p.p_partkey
WHERE
    l.l_shipdate >= DATE '1995-09-01'
    AND l.l_shipdate < DATE '1995-10-01';
```

# Insights e Análises

1. ANÁLISE DE PROBLEMAS
   A consulta original é lenta principalmente devido à provável ausência de índices nas colunas utilizadas nas condições de JOIN e WHERE. Isso leva o otimizador do PostgreSQL a escolher planos de execução ineficientes:

Scans Sequenciais (Seq Scan): Sem índices em l_shipdate, l_partkey, p_partkey e p_type, o otimizador do PostgreSQL provavelmente recorrerá a varreduras sequenciais completas (Seq Scan) nas tabelas lineitem e part. Isso significa que cada linha de ambas as tabelas precisará ser lida do disco para verificar as condições, o que é extremamente ineficiente para tabelas grandes. Conforme o manual do PostgreSQL (pág. 568.0), um Bitmap Heap Scan ou Index Scan é geralmente mais eficiente do que um Seq Scan quando apenas uma parte dos dados é necessária. O custo de uma varredura sequencial é geralmente menor por página (seq_page_cost) do que uma varredura aleatória (random_page_cost), mas o custo total pode ser muito maior se muitas páginas precisarem ser lidas (pág. 710.0).
Ineficiência no JOIN: A condição l_partkey = p_partkey é a chave para a junção entre as tabelas lineitem e part. Sem índices nessas colunas, o PostgreSQL pode ser forçado a usar um Hash Join (que requer construir uma tabela hash em memória ou em disco) ou um Nested Loop Join com varreduras sequenciais, ambos caros para grandes volumes de dados. Índices nessas colunas permitiriam junções mais eficientes, como Merge Join (se os dados já estiverem ordenados ou puderem ser rapidamente ordenados via índice) ou Nested Loop com Index Scan (pág. 493.0).
Filtragem de Data Lenta: A condição l_shipdate >= '1995-09-01' AND l_shipdate < '1995-09-01' + interval '1 month' é um filtro de intervalo. Sem um índice em l_shipdate, o banco de dados precisa escanear todas as linhas da tabela lineitem para encontrar aquelas que se encaixam no intervalo de datas. Um índice B-tree em l_shipdate tornaria essa operação um Index Scan ou Bitmap Index Scan, localizando rapidamente as linhas relevantes (pág. 568.0).
Filtragem de Padrão Lenta: A condição p_type LIKE 'PROMO%' é um filtro de padrão. Embora o operador LIKE com um padrão ancorado à esquerda ('PROMO%') possa utilizar um índice B-tree (pág. 493.0), a ausência de um índice em p_type fará com que o PostgreSQL realize uma varredura sequencial na tabela part para aplicar este filtro. 2. CONSULTA OTIMIZADA
SELECT
100.00 _ SUM(CASE
WHEN p.p_type LIKE 'PROMO%'
THEN l.l_extendedprice _ (1 - l.l_discount)
ELSE 0
END) / SUM(l.l_extendedprice \* (1 - l.l_discount)) AS promo_revenue
FROM
public.lineitem AS l
INNER JOIN
public.part AS p ON l.l_partkey = p.p_partkey
WHERE
l.l_shipdate >= DATE '1995-09-01'
AND l.l_shipdate < DATE '1995-10-01'; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
Mudanças Feitas:

Uso de INNER JOIN Explícito: A sintaxe FROM table1, table2 WHERE table1.col = table2.col é um INNER JOIN implícito. A reescrita para FROM table1 INNER JOIN table2 ON table1.col = table2.col torna a intenção da junção mais clara e é considerada uma boa prática, embora o otimizador do PostgreSQL geralmente trate ambas as formas de maneira idêntica em termos de plano de execução.

Simplificação da Condição de Data: A expressão date '1995-09-01' + interval '1 month' foi simplificada para DATE '1995-10-01'. Isso pode ajudar o otimizador a reconhecer a condição como um limite fixo mais facilmente, embora o PostgreSQL seja geralmente inteligente o suficiente para otimizar a expressão interval.

Recomendação de Índices (Crucial): As principais otimizações virão da criação de índices B-tree nas colunas envolvidas nas condições de WHERE e JOIN.

CREATE INDEX idx_lineitem_shipdate_partkey ON public.lineitem (l_shipdate, l_partkey); Este índice composto é crucial. Ele permitirá que o PostgreSQL realize um Index Scan ou Bitmap Index Scan na tabela lineitem para filtrar rapidamente as linhas pelo l_shipdate dentro do intervalo especificado. Como l_partkey também está incluído no índice, os valores de l_partkey necessários para a junção podem ser lidos diretamente do índice, potencialmente em ordem, o que é benéfico para um Merge Join ou Nested Loop eficiente.
CREATE INDEX idx_part_partkey_type ON public.part (p_partkey, p_type); Este índice composto é igualmente importante. Ele permitirá que o PostgreSQL acesse a tabela part de forma eficiente. Para cada l_partkey da tabela lineitem (após o filtro de data), o otimizador pode usar este índice para encontrar rapidamente o p_partkey correspondente e, crucialmente, verificar a condição p_type LIKE 'PROMO%' diretamente do índice, sem precisar acessar a página de dados da tabela (heap) se a condição for satisfeita pelo índice (potencial Index-Only Scan, se todas as colunas necessárias estiverem no índice e não houver tuplas mortas).
Plano de Execução Estimado:

Com os índices propostos, o PostgreSQL provavelmente processará a nova consulta da seguinte forma, em contraste com a consulta original sem índices:

Consulta Original (sem índices):

Seq Scan em lineitem: O PostgreSQL faria uma varredura sequencial completa na tabela lineitem para encontrar todas as linhas que satisfazem a condição l_shipdate.
Seq Scan em part: Similarmente, faria uma varredura sequencial completa na tabela part para encontrar todas as linhas que satisfazem p_type LIKE 'PROMO%'.
Hash Join ou Nested Loop (lento): As duas tabelas seriam então unidas, provavelmente usando um Hash Join (construindo uma tabela hash a partir de uma das tabelas) ou um Nested Loop com varreduras sequenciais, o que é muito caro em termos de I/O e CPU para grandes tabelas.
Agregação: Após a junção e filtragem, a agregação seria realizada sobre um conjunto potencialmente grande de dados intermediários.
Impacto: Alto custo de I/O devido a múltiplas varreduras sequenciais, alto uso de CPU para junção e filtragem em memória.
Consulta Otimizada (com índices):

Index Scan em lineitem: O PostgreSQL iniciaria com um Index Scan no índice idx_lineitem_shipdate_partkey. Ele usaria a condição l_shipdate >= '1995-09-01' AND l_shipdate < '1995-10-01' para navegar diretamente para as entradas relevantes no índice. Isso reduz drasticamente o número de blocos de disco a serem lidos da tabela lineitem (pág. 568.0).
Junção Eficiente:
Merge Join: Se os dados de l_partkey forem lidos em ordem do índice idx_lineitem_shipdate_partkey e os dados de p_partkey também puderem ser lidos em ordem do índice idx_part_partkey_type, o otimizador pode optar por um Merge Join, que é muito eficiente para grandes conjuntos de dados ordenados.
Nested Loop com Index Scan: Alternativamente, para cada linha filtrada de lineitem, o PostgreSQL pode realizar um Index Scan no índice idx_part_partkey_type para encontrar rapidamente a(s) linha(s) correspondente(s) em part e aplicar o filtro p_type LIKE 'PROMO%'. Este seria um Nested Loop muito mais eficiente do que sem índices.
Filtragem p_type Otimizada: A condição p_type LIKE 'PROMO%' seria aplicada durante o Index Scan na tabela part (usando idx_part_partkey_type), permitindo que o filtro seja aplicado o mais cedo possível, reduzindo o número de linhas a serem processadas. Conforme o manual (pág. 493.0), um índice B-tree pode ser usado para padrões LIKE ancorados à esquerda.
Agregação: A agregação será realizada sobre um conjunto de dados significativamente menor e já filtrado, resultando em um custo de CPU e memória muito menor.
Impacto: Redução drástica do I/O de disco, menor uso de CPU, e tempo de execução da consulta significativamente mais rápido. A preferência por Index Scans em vez de Seq Scans é uma otimização fundamental (pág. 710.0).
Recomendações de Manutenção:

VACUUM ANALYZE: Após a criação dos índices, é fundamental executar VACUUM ANALYZE nas tabelas lineitem e part. O ANALYZE coleta estatísticas de distribuição de dados para o otimizador de consultas, permitindo que ele escolha os planos de execução mais eficientes. O VACUUM limpa tuplas mortas, o que é importante para a performance dos índices e para evitar o inchaço da tabela. A execução regular de ANALYZE (ou a confiança no autovacuum) é crucial para manter as estatísticas atualizadas, especialmente se os dados nas tabelas mudarem frequentemente.

# Consulta Otimizada

```sql
-- Consulta Otimizada
SELECT
    c_name,
    c_acctbal
FROM
    public.customer
WHERE
    c_name ILIKE 'CUSTOMER#000000001%';

-- Sugestão de Índice para máxima performance:
-- Este índice permitirá que a consulta otimizada utilize um Index Scan ou Bitmap Index Scan.
-- CREATE INDEX idx_customer_c_name ON public.customer (c_name);

-- Alternativamente, se a intenção de UPPER() fosse estritamente manter a semântica original
-- e não apenas case-insensitivity, um índice funcional poderia ser criado:
-- CREATE INDEX idx_customer_c_name_upper ON public.customer (UPPER(c_name));
-- No entanto, para case-insensitivity, ILIKE com um índice padrão é geralmente mais performático e flexível.
```

# Insights e Análises

Como especialista em banco de dados PostgreSQL, analisei a consulta fornecida e preparei uma otimização detalhada.

1. ANÁLISE DE PROBLEMAS
   A consulta original é lenta principalmente devido à condição na cláusula WHERE: UPPER(c_name) LIKE 'CUSTOMER#000000001%'.

Não-SARGability: A aplicação da função UPPER() diretamente na coluna c_name torna a condição não-SARGable (Search Argument-able). Isso significa que o otimizador de consultas do PostgreSQL não pode utilizar um índice B-tree padrão criado na coluna c_name de forma eficiente. Para cada linha da tabela, o PostgreSQL precisaria calcular o valor de UPPER(c_name) antes de poder comparar com o padrão LIKE.
Custo de Varredura Sequencial (Seq Scan): Devido à não-SARGability, o PostgreSQL provavelmente recorrerá a um Seq Scan (varredura sequencial) completo na tabela public.customer. Isso implica ler todas as linhas da tabela, aplicar a função UPPER() em cada c_name, e então realizar a comparação LIKE. Para tabelas grandes, um Seq Scan é extremamente custoso em termos de I/O e CPU, resultando em tempos de execução elevados.
Ineficiência do LIKE com função: Embora o operador LIKE 'prefix%' seja geralmente otimizado para usar índices (se a coluna for SARGable), a presença da função UPPER() anula essa otimização, forçando uma avaliação linha a linha.
O contexto do manual fornecido ("Aviso: Banco de dados RAG não inicializado...") não oferece informações adicionais para esta análise específica, portanto, a avaliação é baseada nos princípios fundamentais de otimização do PostgreSQL.

2. CONSULTA OTIMIZADA
   Para otimizar esta consulta, a abordagem mais eficaz é remover a função da coluna na cláusula WHERE e, se necessário, criar um índice adequado. A intenção da consulta original parece ser uma busca case-insensitive (insensível a maiúsculas/minúsculas). O PostgreSQL oferece o operador ILIKE para esse fim, que é SARGable.

-- Consulta Otimizada
SELECT
c_name,
c_acctbal
FROM
public.customer
WHERE
c_name ILIKE 'CUSTOMER#000000001%';

-- Sugestão de Índice para máxima performance:
-- Este índice permitirá que a consulta otimizada utilize um Index Scan ou Bitmap Index Scan.
-- CREATE INDEX idx_customer_c_name ON public.customer (c_name);

-- Alternativamente, se a intenção de UPPER() fosse estritamente manter a semântica original
-- e não apenas case-insensitivity, um índice funcional poderia ser criado:
-- CREATE INDEX idx_customer_c_name_upper ON public.customer (UPPER(c_name));
-- No entanto, para case-insensitivity, ILIKE com um índice padrão é geralmente mais performático e flexível. 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
Explicação das Mudanças:

A principal mudança foi a substituição de UPPER(c_name) LIKE '...' por c_name ILIKE '...'.

ILIKE: Este operador é a versão case-insensitive do LIKE no PostgreSQL. Ele realiza a comparação de padrões sem distinguir entre maiúsculas e minúsculas, atingindo o mesmo objetivo funcional da combinação UPPER() LIKE.
SARGability Restaurada: Ao remover a função UPPER() da coluna c_name, a condição c_name ILIKE '...' torna-se SARGable. Isso permite que o otimizador de consultas considere e utilize um índice B-tree padrão criado na coluna c_name.
Impacto no Plano de Execução Estimado:

Consulta Original (Lenta):

Plano de Execução Provável: Seq Scan na tabela public.customer.
Detalhes: O PostgreSQL teria que ler todas as páginas de dados da tabela public.customer. Para cada tupla (linha) lida, ele executaria a função UPPER() no valor de c_name e, em seguida, aplicaria a comparação LIKE. Este processo é intensivo em I/O e CPU, especialmente para tabelas grandes, resultando em um alto custo de execução.
Consulta Otimizada (Com Índice idx_customer_c_name):

Plano de Execução Provável: Index Scan ou Bitmap Index Scan no índice idx_customer_c_name, seguido por Heap Fetch (se necessário).
Detalhes:
O PostgreSQL utilizaria o índice idx_customer_c_name para localizar rapidamente as tuplas que satisfazem a condição c_name ILIKE 'CUSTOMER#000000001%'.
Um Index Scan percorreria as entradas do índice que correspondem ao padrão, obtendo os ctid (identificadores de tupla) das linhas correspondentes.
Em seguida, ele faria um Heap Fetch para buscar as colunas c_name e c_acctbal da tabela principal (heap) apenas para as tuplas identificadas pelo índice.
Impacto Previsto: Esta mudança transformará uma operação de varredura completa da tabela em uma busca direcionada no índice, reduzindo drasticamente o número de blocos de dados a serem lidos e processados. O custo de I/O e CPU será significativamente menor, resultando em uma execução muito mais rápida, especialmente em tabelas com milhões de linhas onde a seletividade da condição WHERE é alta (ou seja, poucas linhas correspondem ao padrão).
Recomendações de Manutenção:

Para garantir que o PostgreSQL continue a usar os planos de execução mais eficientes e que os índices permaneçam eficazes, as seguintes recomendações de manutenção são cruciais:

ANALYZE: Execute ANALYZE public.customer; regularmente (ou confie no autovacuum para fazer isso). O ANALYZE coleta estatísticas sobre a distribuição de dados nas colunas da tabela. Estatísticas precisas são vitais para o otimizador de consultas escolher o melhor plano de execução (por exemplo, decidir se um Index Scan é mais eficiente que um Seq Scan).
VACUUM: Execute VACUUM public.customer; regularmente (ou confie no autovacuum). O VACUUM recupera espaço de tuplas "mortas" (linhas que foram atualizadas ou excluídas) e atualiza o mapa de visibilidade da tabela. Isso é essencial para manter a eficiência dos índices e evitar o "table bloat" (inchaço da tabela), que pode degradar a performance de varreduras e o uso de índices.
REINDEX: Se o índice idx_customer_c_name sofrer de inchaço significativo ao longo do tempo (devido a muitas atualizações/exclusões), um REINDEX pode ser considerado para reconstruí-lo e otimizar seu tamanho e estrutura. No entanto, isso é menos frequente que ANALYZE e VACUUM.

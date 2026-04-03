# Consulta Otimizada

```sql
SELECT
    ps_partkey,
    value
FROM (
    SELECT
        ps_partkey,
        sum(ps_supplycost * ps_availqty) AS value,
        sum(sum(ps_supplycost * ps_availqty)) OVER () AS total_germany_value
    FROM
        partsupp
    JOIN
        supplier ON ps_suppkey = s_suppkey
    JOIN
        nation ON s_nationkey = n_nationkey
    WHERE
        n_name = 'GERMANY'
    GROUP BY
        ps_partkey
) AS grouped_values_with_total
WHERE
    value > total_germany_value * 0.0001000000
ORDER BY
    value DESC;
```

# Insights e Análises

PAPEL
Você é um especialista em banco de dados PostgreSQL. Sua tarefa é transformar consultas lentas em consultas de alta performance.

ENTRADAS
CONSULTA ORIGINAL:
select
ps*partkey,
sum(ps_supplycost * ps*availqty) as value
from
partsupp,
supplier,
nation
where
ps_suppkey = s_suppkey
and s_nationkey = n_nationkey
and n_name = 'GERMANY'
group by
ps_partkey having
sum(ps_supplycost * ps*availqty) > (
select
sum(ps_supplycost * ps*availqty) * 0.0001000000
from
partsupp,
supplier,
nation
where
ps_suppkey = s_suppkey
and s_nationkey = n_nationkey
and n_name = 'GERMANY'
)
order by
value desc;
SCHEMAS DAS TABELAS:
partsupp
CREATE TABLE IF NOT EXISTS public.partsupp
(
ps_partkey integer NOT NULL,
ps_suppkey integer NOT NULL,
ps_availqty integer NOT NULL,
ps_supplycost numeric(15,2) NOT NULL,
ps_comment character varying(199) COLLATE pg_catalog."default" NOT NULL
)
supplier
CREATE TABLE IF NOT EXISTS public.supplier
(
s_suppkey integer NOT NULL,
s_name character(25) COLLATE pg_catalog."default" NOT NULL,
s_address character varying(40) COLLATE pg_catalog."default" NOT NULL,
s_nationkey integer NOT NULL,
s_phone character(15) COLLATE pg_catalog."default" NOT NULL,
s_acctbal numeric(15,2) NOT NULL,
s_comment character varying(101) COLLATE pg_catalog."default" NOT NULL
)
nation
CREATE TABLE IF NOT EXISTS public.nation
(
n_nationkey integer NOT NULL,
n_name character(25) COLLATE pg_catalog."default" NOT NULL,
n_regionkey integer NOT NULL,
n_comment character varying(152) COLLATE pg_catalog."default"
)
TAREFA
Analise a consulta e forneça uma resposta estruturada em três partes:

ANÁLISE DE PROBLEMAS:

Identifique por que a consulta original é lenta.
Cite conceitos como SARGability, tipos de Joins, ou custo de ordenação se aplicável.
Use as informações do MANUAL fornecidas para validar sua análise.
AO CITAR O MANUAL: Não repita o conteúdo bruto (trechos) do manual na resposta. Em vez disso, mencione apenas o número da página correspondente como referência (ex: "Conforme o manual do PostgreSQL (pág. 42)...").
CONSULTA OTIMIZADA:

Forneça APENAS o código SQL reescrito para máxima performance dentro do bloco de código.
NÃO inclua comentários de sugestão de índices dentro do bloco SQL.
Mantenha a semântica original dos dados.
Se houver necessidade de índices, mencione-os APENAS na seção 3 (EXPLICAÇÃO TÉCNICA).
EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO:

Explique as mudanças feitas.
Descreva como o PostgreSQL provavelmente processará a nova consulta comparada à antiga, explicando também o impacto previsto (ex: "Mudança de Seq Scan para Index Scan").
Forneça recomendações de manutenção (VACUUM, ANALYZE).
REGRAS CRÍTICAS
Responda em PORTUGUÊS. Todas as citações, referências e explicações baseadas no MANUAL (RAG) que estiverem em outros idiomas DEVEM ser traduzidas para o Português do Brasil de forma clara e técnica.
REFERÊNCIAS AO MANUAL: Nunca exiba o conteúdo bruto dos trechos do MANUAL na sua resposta. Utilize apenas o número da página para referenciar o conhecimento aplicado.
Seja extremamente técnico e preciso.
Se a consulta for ineficiente devido à estrutura (ex: falta de índices), forneça o comando CREATE INDEX.
Utilize o contexto do MANUAL sempre que possível para embasar sua decisão.

1. ANÁLISE DE PROBLEMAS:
   A consulta original apresenta um gargalo de performance significativo devido à execução redundante de operações de junção e agregação. Os principais problemas são:

Execução Duplicada de Lógica: A subconsulta aninhada na cláusula HAVING é uma réplica exata da lógica de FROM, JOIN, WHERE e SUM da consulta principal. Isso força o PostgreSQL a executar as operações de junção entre partsupp, supplier e nation, a filtragem por n*name = 'GERMANY' e o cálculo da soma agregada (sum(ps_supplycost * ps*availqty)) duas vezes. Essa duplicação de trabalho gera um custo computacional e de I/O desnecessariamente alto. Embora o planejador de consultas possa otimizar algumas subconsultas, a repetição de uma lógica complexa como esta geralmente resulta em subplanos que são executados independentemente, conforme o manual do PostgreSQL sugere que subconsultas podem levar a subplanos (pág. 710).
Custo de Agregação e Junção: Ambas as instâncias da consulta (principal e subconsulta) envolvem junções de três tabelas e uma agregação que requer o cálculo de ps_supplycost * ps*availqty para cada linha qualificada. Em tabelas grandes, como partsupp, essas operações são inerentemente custosas, e sua duplicação agrava o problema.
Potencial para Sort Explícito: A cláusula ORDER BY value DESC, onde value é um resultado de agregação (sum(ps_supplycost * ps*availqty)), provavelmente exigirá um passo de ordenação explícito (Sort) após a agregação. Isso ocorre porque um índice em ps_partkey (usado para GROUP BY) não garante a ordem do valor agregado value, a menos que haja uma correlação muito forte e específica que o planejador possa inferir, o que é raro para somas. O manual do PostgreSQL explica que um ORDER BY em um agregado geralmente requer um passo de Sort separado (pág. 497, 569). 2. CONSULTA OTIMIZADA:
SELECT
ps_partkey,
value
FROM (
SELECT
ps_partkey,
sum(ps_supplycost * ps*availqty) AS value,
sum(sum(ps_supplycost * ps*availqty)) OVER () AS total_germany_value
FROM
partsupp
JOIN
supplier ON ps_suppkey = s_suppkey
JOIN
nation ON s_nationkey = n_nationkey
WHERE
n_name = 'GERMANY'
GROUP BY
ps_partkey
) AS grouped_values_with_total
WHERE
value > total_germany_value * 0.0001000000
ORDER BY
value DESC; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO:
Explicação das Mudanças:

A otimização central desta consulta reside na eliminação da execução redundante da lógica de junção e agregação. Isso foi alcançado através da utilização de uma função de janela (SUM(...) OVER ()) dentro de uma subconsulta derivada.

Agregação Única: A subconsulta interna (grouped*values_with_total) executa as junções (partsupp, supplier, nation) e a filtragem (n_name = 'GERMANY') uma única vez. Em seguida, calcula a soma sum(ps_supplycost * ps*availqty) agrupada por ps_partkey.
Cálculo do Total com Função de Janela: Dentro da mesma subconsulta, sum(sum(ps_supplycost * ps_availqty)) OVER () é empregado para calcular a soma total de value (que já representa a soma agrupada de cada ps_partkey) sobre todos os resultados da agregação interna. Esta operação de função de janela é executada após a cláusula GROUP BY, permitindo que o total_germany_value seja calculado uma única vez sobre o conjunto de resultados já agregados, evitando a reexecução completa das junções e agregações.
Filtragem Eficiente: A condição HAVING original é convertida em uma cláusula WHERE na consulta externa. Esta cláusula compara o value de cada grupo com o total_germany_value (calculado de forma eficiente pela função de janela), garantindo que a filtragem seja aplicada após todos os cálculos necessários terem sido realizados uma única vez.
Impacto Previsto no Plano de Execução:

O PostgreSQL provavelmente processará a nova consulta de forma significativamente mais eficiente:

Leitura e Filtragem Inicial (Subconsulta Interna):

O planejador iniciará com um Index Scan ou Bitmap Index Scan na tabela nation para identificar as linhas onde n_name = 'GERMANY' (utilizando idx_nation_name).
Em seguida, nation será unida a supplier através de n_nationkey e s_nationkey (provavelmente usando idx_nation_nkey e idx_supplier_nkey_skey).
Finalmente, supplier será unida a partsupp usando s_suppkey e ps_suppkey (utilizando idx_supplier_nkey_skey e idx_partsupp_skey_pkey_include).
Essas operações de junção e filtragem serão executadas apenas uma vez, ao contrário da consulta original que as repetia.
Agregação e Função de Janela:

Após as junções e filtragem, os dados serão agrupados por ps_partkey. Isso pode ser realizado por um HashAggregate ou GroupAggregate, dependendo da cardinalidade dos dados e da presença de índices adequados.
Em um passo subsequente, um nó WindowAgg será executado sobre os resultados já agrupados para calcular o total_germany_value usando a função de janela SUM(...) OVER (). Este cálculo é muito mais leve do que reexecutar toda a consulta.
Filtragem Final e Ordenação (Consulta Externa):

A cláusula WHERE value > total_germany_value \* 0.0001000000 será aplicada aos resultados da subconsulta.
Um Sort explícito será realizado para satisfazer o ORDER BY value DESC. Como value é um valor agregado, um índice em ps_partkey não pode diretamente satisfazer esta ordenação, e um passo de ordenação final será necessário (pág. 497, 569).
Recomendações de Manutenção:

Para maximizar o desempenho da consulta otimizada, os seguintes índices são cruciais:

CREATE INDEX idx_nation_name ON nation (n_name);
Justificativa: Acelera a filtragem inicial por n_name = 'GERMANY', permitindo um Index Scan direto na tabela nation.
CREATE INDEX idx_nation_nkey ON nation (n_nationkey);
Justificativa: Otimiza a junção entre nation e supplier na coluna n_nationkey.
CREATE INDEX idx_supplier_nkey_skey ON supplier (s_nationkey, s_suppkey);
Justificativa: Este índice composto otimiza duas junções importantes: a junção entre supplier e nation (usando s_nationkey) e a junção entre supplier e partsupp (usando s_suppkey). Índices multicolunas podem ser muito eficazes para condições AND em junções (pág. 497).
CREATE INDEX idx_partsupp_skey_pkey_include ON partsupp (ps_suppkey, ps_partkey) INCLUDE (ps_supplycost, ps_availqty);
Justificativa: Este índice composto otimiza a junção entre partsupp e supplier (na coluna ps_suppkey) e auxilia no agrupamento por ps_partkey. As colunas ps_supplycost e ps_availqty são incluídas para permitir um Index-Only Scan (pág. 8). Isso significa que o PostgreSQL pode, em muitos casos, obter todos os dados necessários para a agregação diretamente do índice, evitando acessos caros à tabela principal (heap) e reduzindo significativamente o I/O.
Além dos índices, é fundamental manter as estatísticas do planejador de consultas atualizadas:

ANALYZE: Execute ANALYZE regularmente em todas as tabelas envolvidas (partsupp, supplier, nation). Estatísticas precisas são vitais para que o planejador de consultas escolha o plano de execução mais eficiente. Estatísticas desatualizadas podem levar a estimativas de custo incorretas e, consequentemente, a planos subótimos.
VACUUM (ou AUTOVACUUM): Garanta que o autovacuum esteja configurado e funcionando adequadamente. VACUUM é essencial para remover tuplas mortas, liberar espaço e manter o visibility map atualizado. Um visibility map bem mantido é crucial para a eficiência de Index-Only Scans e para prevenir o inchaço da tabela, o que impacta diretamente o desempenho de I/O.
A aplicação dessas otimizações e a manutenção adequada do banco de dados transformarão a consulta de uma operação lenta e redundante em um processo linear, eficiente e de alta performance.

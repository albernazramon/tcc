# Consulta Otimizada

```sql
select
	sum(l_extendedprice * l_discount) as revenue
from
	lineitem
where
	l_shipdate >= '1994-01-01'
	and l_shipdate < '1995-01-01'
	and l_discount between 0.05 and 0.07
	and l_quantity < 24;
```

# Insights e Análises

ANÁLISE DE PROBLEMAS:
A consulta original é lenta principalmente devido à ausência de índices na tabela lineitem. Sem índices, o planejador de consultas do PostgreSQL é forçado a realizar um Seq Scan (varredura sequencial) em toda a tabela para avaliar as condições da cláusula WHERE. Isso significa que cada linha da tabela precisa ser lida e verificada, o que é extremamente ineficiente para tabelas grandes, especialmente quando a consulta é seletiva e retorna apenas uma pequena fração das linhas.

As condições de filtro na cláusula WHERE são todas SARGable (Search Argument-able), ou seja, elas podem ser diretamente utilizadas por um índice para localizar rapidamente as linhas. As condições são:

l_shipdate >= date '1994-01-01' and l_shipdate < date '1994-01-01' + interval '1 year' (filtro de intervalo de datas)
l_discount between .06 - 0.01 and .06 + 0.01 (filtro de intervalo numérico)
l_quantity < 24 (filtro de limite numérico)
Conforme o manual do PostgreSQL (pág. 573.0), quando uma tabela não possui índices, o Seq Scan é a única opção disponível para o planejador de consultas. Isso resulta em um alto custo de I/O, pois todas as páginas de disco da tabela precisam ser lidas, independentemente da quantidade de dados que realmente satisfazem os critérios. O custo de acesso sequencial a páginas de disco (seq_page_cost) é geralmente menor que o custo de acesso aleatório (random_page_cost), mas o volume total de páginas lidas em um Seq Scan pode ser proibitivo para tabelas grandes (pág. 710.0).

A falta de índices impede o planejador de utilizar estratégias mais eficientes, como Bitmap Index Scan ou Index Scan, que são projetadas para localizar rapidamente as linhas relevantes usando uma estrutura de índice e, em seguida, buscar apenas os dados necessários da tabela (pág. 568.0).

CONSULTA OTIMIZADA:
select
sum(l_extendedprice \* l_discount) as revenue
from
lineitem
where
l_shipdate >= '1994-01-01'
and l_shipdate < '1995-01-01'
and l_discount between 0.05 and 0.07
and l_quantity < 24;
EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO:
Mudanças Feitas: A consulta SQL otimizada é semanticamente idêntica à original. As únicas alterações foram pequenas simplificações nas condições WHERE para maior clareza (ex: date '1994-01-01' + interval '1 year' para '1995-01-01', e o cálculo do BETWEEN para 0.05 e 0.07). Essas simplificações não alteram o plano de execução, mas tornam a consulta mais legível. A principal otimização reside na recomendação de índices.

Recomendação de Índice: Para transformar esta consulta em uma de alta performance, é crucial criar um índice composto nas colunas utilizadas nas condições WHERE. A ordem das colunas no índice é importante para otimizar o uso do índice em consultas de intervalo. Recomenda-se o seguinte índice:

CREATE INDEX idx_lineitem_shipdate_discount_quantity ON public.lineitem (l_shipdate, l_discount, l_quantity);
Explicação Técnica e Impacto: Com a criação do índice idx_lineitem_shipdate_discount_quantity, o PostgreSQL poderá utilizar uma estratégia de Index Scan ou Bitmap Index Scan em vez do ineficiente Seq Scan.

Plano de Execução Antigo (sem índice):

Seq Scan on lineitem: O planejador de consultas seria forçado a ler a tabela lineitem inteira, linha por linha, para aplicar todos os filtros (l_shipdate, l_discount, l_quantity). Este processo é caro em termos de I/O e CPU, especialmente para tabelas grandes, pois o custo de acesso sequencial a páginas de disco é aplicado a todas as páginas da tabela (pág. 573.0, pág. 710.0).
Filter: Após a leitura, as condições WHERE seriam aplicadas para descartar as linhas que não correspondem.
Aggregate: Finalmente, a função SUM seria calculada sobre as linhas restantes.
Plano de Execução Estimado (com índice):

Bitmap Index Scan on idx_lineitem_shipdate_discount_quantity: O planejador usará o índice para localizar rapidamente os TIDs (Tuple IDs) das linhas que satisfazem todas as condições WHERE (l_shipdate >= '1994-01-01' AND l_shipdate < '1995-01-01' AND l_discount BETWEEN 0.05 AND 0.07 AND l_quantity < 24). O índice B-tree é altamente eficiente para condições de intervalo e igualdade (pág. 493.0). O PostgreSQL pode combinar múltiplas condições de índice usando operações AND/OR em varreduras de bitmap (pág. 497.0).
Bitmap Heap Scan on lineitem: Após identificar os TIDs das linhas relevantes através do índice, o PostgreSQL acessará apenas as páginas de dados da tabela (heap) que contêm essas linhas. Isso evita a leitura de páginas de dados desnecessárias, reduzindo drasticamente o I/O. As colunas l_extendedprice e l_discount (necessárias para o cálculo do SUM) serão então recuperadas dessas linhas (pág. 568.0).
Aggregate: A função SUM(l_extendedprice \* l_discount) será calculada sobre o conjunto de linhas filtradas e recuperadas.
Impacto Previsto: A mudança de um Seq Scan para um Bitmap Index Scan seguido por um Bitmap Heap Scan resultará em uma melhoria significativa de performance. O tempo de execução da consulta será drasticamente reduzido, especialmente em tabelas lineitem grandes, pois o número de blocos de disco lidos será minimizado. O custo de acesso aleatório a páginas de disco, embora maior por página individualmente, será aplicado a um número muito menor de páginas, tornando a operação total muito mais barata (pág. 710.0).

Recomendações de Manutenção:

ANALYZE: Após a criação do índice e periodicamente, execute ANALYZE lineitem; para garantir que o planejador de consultas tenha estatísticas atualizadas sobre a distribuição dos dados na tabela e no novo índice. Estatísticas precisas são cruciais para que o planejador escolha o plano de execução mais eficiente.
VACUUM: Mantenha a tabela lineitem regularmente VACUUMada (ou use autovacuum) para remover tuplas mortas e manter a tabela e os índices eficientes. Isso é importante para o desempenho geral e para garantir que o Bitmap Heap Scan seja o mais eficiente possível.

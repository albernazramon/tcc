# Consulta Otimizada

```sql
select
	l_shipmode,
	sum(case
		when o_orderpriority = '1-URGENT'
			or o_orderpriority = '2-HIGH'
			then 1
		else 0
	end) as high_line_count,
	sum(case
		when o_orderpriority <> '1-URGENT'
			and o_orderpriority <> '2-HIGH'
			then 1
		else 0
	end) as low_line_count
from
	orders,
	lineitem
where
	o_orderkey = l_orderkey
	and l_shipmode in ('MAIL', 'SHIP')
	and l_commitdate < l_receiptdate
	and l_shipdate < l_commitdate
	and l_receiptdate >= date '1994-01-01'
	and l_receiptdate < date '1994-01-01' + interval '1 year'
group by
	l_shipmode
order by
	l_shipmode;
```

# Insights e Análises

Como especialista em banco de dados PostgreSQL, analisei a consulta fornecida e os schemas das tabelas para identificar gargalos de performance e propor otimizações.

1. ANÁLISE DE PROBLEMAS
   A consulta original apresenta vários problemas de performance, principalmente devido à provável ausência de índices nas tabelas orders e lineitem, o que leva a operações de I/O ineficientes e processamento excessivo de dados.

Scans Sequenciais (Seq Scan) em Tabelas Grandes: Sem índices, o PostgreSQL provavelmente realizará varreduras sequenciais completas (Seq Scan) nas tabelas orders e lineitem para satisfazer as condições de WHERE e a cláusula JOIN. Para tabelas grandes, isso é extremamente custoso, pois exige a leitura de todos os blocos de dados do disco, mesmo que apenas uma pequena fração das linhas seja relevante (Conforme o manual do PostgreSQL, pág. 569, 15, 16).
Ineficiência na Cláusula WHERE: As condições de filtro na tabela lineitem (l_shipmode, l_commitdate, l_receiptdate, l_shipdate) são seletivas. Sem índices apropriados, o planejador de consultas não pode usar uma busca de índice (Index Scan ou Bitmap Index Scan) para localizar rapidamente as linhas correspondentes. Em vez disso, ele terá que aplicar esses filtros a cada linha lida durante o Seq Scan, desperdiçando recursos de CPU e I/O. As condições de data (l_receiptdate >= date '1994-01-01' and l_receiptdate < date '1995-01-01') são ideais para serem aceleradas por um índice B-tree (Conforme o manual do PostgreSQL, pág. 493).
Custo da Operação JOIN: A junção entre orders e lineitem na coluna o_orderkey = l_orderkey será ineficiente sem índices nessas colunas. O planejador pode optar por um Hash Join ou Nested Loop Join com varreduras sequenciais, que são caros para grandes volumes de dados. Um Nested Loop Join sem um índice na tabela interna (neste caso, orders.o_orderkey) resultaria em um Seq Scan para cada linha da tabela externa, o que é proibitivo (Conforme o manual do PostgreSQL, pág. 573).
Custo de Ordenação (ORDER BY e GROUP BY): A consulta inclui GROUP BY l_shipmode e ORDER BY l_shipmode. Sem um índice que forneça os dados já ordenados por l_shipmode, o PostgreSQL precisará realizar uma etapa de ordenação explícita (Sort ou GroupAggregate com sort) após a junção e filtragem dos dados. Essa operação pode consumir muita memória e, se os dados excederem a memória disponível, pode resultar em despejo para disco, aumentando drasticamente o tempo de execução (Conforme o manual do PostgreSQL, pág. 497, 569). 2. CONSULTA OTIMIZADA
A consulta original já está bem estruturada em termos de lógica SQL. A principal otimização virá da adição de índices. Não há necessidade de reescrever a lógica da consulta.

select
l_shipmode,
sum(case
when o_orderpriority = '1-URGENT'
or o_orderpriority = '2-HIGH'
then 1
else 0
end) as high_line_count,
sum(case
when o_orderpriority <> '1-URGENT'
and o_orderpriority <> '2-HIGH'
then 1
else 0
end) as low_line_count
from
orders,
lineitem
where
o_orderkey = l_orderkey
and l_shipmode in ('MAIL', 'SHIP')
and l_commitdate < l_receiptdate
and l_shipdate < l_commitdate
and l_receiptdate >= date '1994-01-01'
and l_receiptdate < date '1994-01-01' + interval '1 year'
group by
l_shipmode
order by
l_shipmode; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
As otimizações propostas focam na criação de índices estratégicos para permitir que o planejador de consultas utilize métodos de acesso mais eficientes.

Índices Recomendados:

orders.o_orderkey:

CREATE INDEX idx_orders_o_orderkey ON public.orders (o_orderkey);
Justificativa: Este índice é crucial para otimizar a cláusula JOIN (o_orderkey = l_orderkey). Ao indexar o_orderkey, o PostgreSQL pode realizar uma busca rápida na tabela orders para cada l_orderkey correspondente, transformando um Nested Loop Join potencialmente lento em uma operação eficiente, ou facilitando um Merge Join ou Hash Join ao permitir acesso rápido aos dados de orders.
lineitem (Índice Composto):

CREATE INDEX idx_lineitem_optimized ON public.lineitem (l_shipmode, l_receiptdate, l_commitdate, l_shipdate, l_orderkey);
Justificativa: Este é um índice composto B-tree projetado para cobrir a maioria das condições da cláusula WHERE, GROUP BY e ORDER BY na tabela lineitem.
l_shipmode (primeira coluna): Permite que o planejador use o índice para a condição l_shipmode IN ('MAIL', 'SHIP') de forma eficiente. Além disso, como é a primeira coluna, ele pode satisfazer as cláusulas GROUP BY l_shipmode e ORDER BY l_shipmode diretamente a partir do índice, evitando uma etapa de ordenação explícita (Conforme o manual do PostgreSQL, pág. 497, 569).
l_receiptdate (segunda coluna): Após filtrar por l_shipmode, este índice permite uma busca eficiente por faixa de datas (l_receiptdate >= '1994-01-01' AND l_receiptdate < '1995-01-01').
l_commitdate, l_shipdate (terceira e quarta colunas): Permitem que as condições l_commitdate < l_receiptdate e l_shipdate < l_commitdate sejam avaliadas diretamente no índice, reduzindo a necessidade de acessar os blocos da tabela (Heap Scan) para essas verificações.
l_orderkey (quinta coluna): Incluir l_orderkey no índice permite que o PostgreSQL obtenha os valores necessários para a junção com a tabela orders diretamente do índice. Isso é crucial para um Index Only Scan na tabela lineitem (se todas as colunas necessárias de lineitem estivessem no índice e o MVCC visibilidade permitisse), ou pelo menos para reduzir o número de acessos à tabela.
Plano de Execução Estimado (com Índices):

Com os índices propostos, o PostgreSQL provavelmente processará a consulta da seguinte forma:

Index Scan (ou Bitmap Index Scan) na lineitem: O planejador utilizará idx_lineitem_optimized para filtrar as linhas de lineitem que satisfazem as condições l_shipmode IN (...), l_receiptdate >= ... AND l_receiptdate < ..., l_commitdate < l_receiptdate e l_shipdate < l_commitdate. Como l_shipmode é a primeira coluna do índice, a busca será muito eficiente. Este passo reduzirá drasticamente o número de linhas a serem processadas.
Impacto: Mudança de Seq Scan para Index Scan ou Bitmap Heap Scan (Conforme o manual do PostgreSQL, pág. 15, 569). Isso significa que apenas os blocos de dados relevantes serão lidos, em vez da tabela inteira.
Junção (Nested Loop Join ou Merge Join): As linhas filtradas de lineitem (que já terão l_orderkey disponível do índice) serão unidas à tabela orders usando o_orderkey. Com idx_orders_o_orderkey, o PostgreSQL pode realizar um Nested Loop Join eficiente, onde para cada l_orderkey da lineitem filtrada, ele faz uma busca rápida no índice de orders para encontrar a linha correspondente. Alternativamente, se os dados já estiverem ordenados de forma compatível, um Merge Join pode ser utilizado.
Impacto: A junção será significativamente mais rápida, evitando varreduras sequenciais repetidas na tabela orders.
Agregação e Ordenação: Após a junção, os resultados serão agrupados por l_shipmode. Como l_shipmode é a primeira coluna de idx_lineitem_optimized e a consulta também tem ORDER BY l_shipmode, o PostgreSQL pode ser capaz de satisfazer a ordenação e o agrupamento com um custo mínimo, possivelmente usando um GroupAggregate que se beneficia da ordem de entrada, ou até mesmo evitando uma etapa de ordenação explícita se os dados já estiverem pré-ordenados pelo Index Scan.
Impacto: Redução ou eliminação do custo de uma etapa de Sort explícita (Conforme o manual do PostgreSQL, pág. 497, 569).
Recomendações de Manutenção:

VACUUM ANALYZE: É crucial executar VACUUM ANALYZE regularmente nas tabelas orders e lineitem após a criação dos índices e após qualquer alteração significativa nos dados (INSERTs, UPDATEs, DELETEs). Isso garante que as estatísticas do planejador de consultas estejam atualizadas, permitindo que ele escolha o plano de execução mais eficiente.
Monitoramento: Monitore o uso dos índices e o desempenho da consulta usando EXPLAIN ANALYZE para garantir que os índices estejam sendo utilizados conforme o esperado e para identificar quaisquer outros gargalos.
REINDEX: Em sistemas com muitas operações de UPDATE/DELETE, os índices B-tree podem sofrer de "bloat" (inchaço), o que pode degradar seu desempenho. Se isso ocorrer, um REINDEX periódico pode ser benéfico.

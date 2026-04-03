# Consulta Otimizada

```sql
select
	l_orderkey,
	sum(l_extendedprice * (1 - l_discount)) as revenue,
	o_orderdate,
	o_shippriority
from
	customer,
	orders,
	lineitem
where
	c_mktsegment = 'BUILDING'
	and c_custkey = o_custkey
	and l_orderkey = o_orderkey
	and o_orderdate < date '1995-03-15'
	and l_shipdate > date '1995-03-15'
group by
	l_orderkey,
	o_orderdate,
	o_shippriority
order by
	revenue desc,
	o_orderdate
limit 10;
```

# Insights e Análises

1. ANÁLISE DE PROBLEMAS
   A consulta original é lenta principalmente devido à ausência de índices adequados nas colunas utilizadas nas cláusulas WHERE, JOIN, GROUP BY e ORDER BY. Isso leva a um processamento ineficiente em várias etapas:

Scans Sequenciais (Seq Scans): Sem índices nas colunas c_mktsegment, o_orderdate e l_shipdate, o planejador de consultas será forçado a realizar varreduras sequenciais completas (Seq Scans) nas tabelas customer, orders e lineitem para aplicar as condições de filtro. Para tabelas grandes, isso é extremamente custoso em termos de I/O e CPU, pois exige a leitura de todos os blocos de dados da tabela. Conforme o manual do PostgreSQL (pág. 573), na ausência de índices, a varredura sequencial é a única opção disponível para o planejador.

Junções Ineficientes: As condições de junção c_custkey = o_custkey e l_orderkey = o_orderkey também sofrem sem índices nas colunas de chave estrangeira (o_custkey e l_orderkey). Embora as chaves primárias (c_custkey e o_orderkey) geralmente sejam indexadas automaticamente, a falta de índices nas chaves estrangeiras impede o uso de métodos de junção eficientes como Index Nested Loop Join. Em vez disso, o planejador pode recorrer a Hash Joins ou Merge Joins que, embora eficientes em alguns cenários, podem exigir varreduras sequenciais e/ou etapas de ordenação prévias, aumentando o custo. O manual do PostgreSQL (pág. 493, 497) destaca a importância de índices para condições de comparação em cláusulas WHERE e, por extensão, em condições de junção.

Ordenação e Agregação Custosas com LIMIT: A consulta realiza um GROUP BY e, em seguida, um ORDER BY revenue DESC, o_orderdate com um LIMIT 10. Como revenue é uma função de agregação (SUM), o banco de dados precisa primeiro calcular a agregação para todos os grupos resultantes das junções e filtros. Após a agregação, ele precisa ordenar todo o conjunto de resultados agregados para identificar os 10 primeiros. Esta etapa de ordenação explícita em um grande volume de dados intermediários é um gargalo significativo. O manual do PostgreSQL (pág. 15, 497, 569) explica que, para consultas com ORDER BY e LIMIT n, um sort explícito terá que processar todos os dados para identificar as primeiras n linhas, a menos que um índice possa fornecer a ordem diretamente. No caso de uma agregação, um índice direto na coluna agregada não é possível.

Falta de Índices de Cobertura: Para a tabela lineitem, as colunas l_extendedprice e l_discount são usadas na agregação. Sem um índice que cubra essas colunas (junto com l_orderkey e l_shipdate), o planejador precisará acessar o heap da tabela para buscar esses valores, mesmo que um Index Scan seja usado para filtrar e juntar. Isso aumenta o custo de I/O.

2. CONSULTA OTIMIZADA
   A consulta SQL em si é semanticamente correta e não precisa de alterações. A otimização será alcançada através da adição de índices.

select
l_orderkey,
sum(l_extendedprice \* (1 - l_discount)) as revenue,
o_orderdate,
o_shippriority
from
customer,
orders,
lineitem
where
c_mktsegment = 'BUILDING'
and c_custkey = o_custkey
and l_orderkey = o_orderkey
and o_orderdate < date '1995-03-15'
and l_shipdate > date '1995-03-15'
group by
l_orderkey,
o_orderdate,
o_shippriority
order by
revenue desc,
o_orderdate
limit 10; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
As mudanças para otimizar esta consulta consistem na criação de índices estratégicos.

Recomendações de Índices:

public.customer:

CREATE INDEX idx_customer_mktsegment ON public.customer (c_mktsegment);
Propósito: Acelerar o filtro c_mktsegment = 'BUILDING'.
CREATE INDEX idx_customer_custkey ON public.customer (c_custkey);
Propósito: Otimizar a junção c_custkey = o_custkey. (Assumindo que c_custkey não é a chave primária, que já seria indexada).
public.orders:

CREATE INDEX idx_orders_custkey ON public.orders (o_custkey);
Propósito: Otimizar a junção c_custkey = o_custkey.
CREATE INDEX idx_orders_orderkey ON public.orders (o_orderkey);
Propósito: Otimizar a junção l_orderkey = o_orderkey. (Assumindo que o_orderkey não é a chave primária, que já seria indexada).
CREATE INDEX idx_orders_orderdate_shippriority ON public.orders (o_orderdate, o_shippriority);
Propósito: Acelerar o filtro o_orderdate < date '1995-03-15' e auxiliar no GROUP BY e ORDER BY nas colunas o_orderdate e o_shippriority. Um índice composto é benéfico quando as colunas são usadas em conjunto para filtragem, agrupamento ou ordenação (Conforme o manual do PostgreSQL, pág. 16, 496, 497).
public.lineitem:

CREATE INDEX idx_lineitem_orderkey_shipdate_include_price_discount ON public.lineitem (l_orderkey, l_shipdate) INCLUDE (l_extendedprice, l_discount);
Propósito: Este é um índice de cobertura. l_orderkey otimiza a junção l_orderkey = o_orderkey e o GROUP BY. l_shipdate acelera o filtro l_shipdate > date '1995-03-15'. As colunas l_extendedprice e l_discount são incluídas para que o cálculo da agregação sum(l_extendedprice \* (1 - l_discount)) possa ser feito diretamente a partir do índice (Index-Only Scan), evitando acessos ao heap da tabela, o que reduz significativamente o I/O (Conforme o manual do PostgreSQL, pág. 1836, que discute a criação de índices em porções específicas da tabela para melhorar a performance).
Plano de Execução Estimado com Índices:

Com os índices propostos, o PostgreSQL provavelmente processará a consulta da seguinte forma:

Filtragem Inicial:

A tabela customer será filtrada usando um Index Scan no idx_customer_mktsegment para encontrar rapidamente os c_custkeys dos clientes do segmento 'BUILDING'.
A tabela orders será filtrada usando um Index Scan no idx_orders_orderdate_shippriority para encontrar os pedidos com o_orderdate < '1995-03-15'.
A tabela lineitem será filtrada usando um Index Scan no idx_lineitem_orderkey_shipdate_include_price_discount para encontrar os itens com l_shipdate > '1995-03-15'. Este índice, sendo de cobertura, permitirá que as colunas l_extendedprice e l_discount sejam lidas diretamente do índice, sem a necessidade de acessar os blocos de dados da tabela (heap), resultando em uma redução drástica de I/O.
Junções Otimizadas:

As junções entre customer e orders (via c_custkey) e entre orders e lineitem (via l_orderkey) serão realizadas de forma muito mais eficiente, provavelmente utilizando Index Nested Loop Joins. Isso é possível porque os filtros iniciais reduzem o número de linhas a serem processadas e os índices nas chaves de junção permitem acesso rápido às linhas correspondentes.
Agregação Eficiente:

Com os dados pré-filtrados e unidos de forma eficiente, a etapa de GROUP BY terá um conjunto de dados de entrada muito menor. O índice idx_orders_orderdate_shippriority e a ordem em que os dados são recuperados pelos Index Scans podem auxiliar o planejador a realizar a agregação (por exemplo, usando um GroupAggregate ou HashAggregate) de forma mais rápida. O PostgreSQL também pode considerar a agregação paralela (Conforme o manual do PostgreSQL, pág. 20, 21), se aplicável, para acelerar ainda mais esta etapa.
Ordenação e Limite Final:

Embora a ordenação final por revenue DESC ainda exija uma etapa de Sort após a agregação (já que revenue é um valor calculado), o volume de dados a ser ordenado será significativamente menor. O LIMIT 10 será aplicado a este conjunto de resultados já ordenado, garantindo que apenas as 10 linhas mais relevantes sejam retornadas. A redução do volume de dados a serem ordenados é crucial para a performance, especialmente com LIMIT (Conforme o manual do PostgreSQL, pág. 15, 497, 569).
Impacto Previsto:

A aplicação desses índices transformará a consulta de uma que provavelmente realiza múltiplos Seq Scans e Hash Joins caros em uma que utiliza Index Scans e Index Nested Loop Joins altamente eficientes. Isso resultará em uma redução drástica no tempo de execução, especialmente em bancos de dados com grandes volumes de dados, devido à minimização de I/O e processamento de CPU.

Recomendações de Manutenção:

ANALYZE: Após a criação dos índices e periodicamente, execute ANALYZE nas tabelas customer, orders e lineitem. Isso garante que o planejador de consultas tenha estatísticas atualizadas sobre a distribuição dos dados e a seletividade dos índices, permitindo-lhe escolher o plano de execução mais eficiente.
VACUUM: Mantenha uma rotina regular de VACUUM (ou autovacuum) para evitar o inchaço das tabelas e índices, e para garantir a visibilidade das tuplas e a reutilização do espaço em disco.

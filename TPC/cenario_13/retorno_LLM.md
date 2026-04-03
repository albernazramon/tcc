# Consulta Otimizada

```sql
select
	c_count,
	count(*) as custdist
from
	(
		select
			c_custkey,
			count(o_orderkey) as c_count
		from
			customer left outer join orders on
				c_custkey = o_custkey
				and o_comment not like '%special%requests%'
		group by
			c_custkey
	) as c_orders
group by
	c_count
order by
	custdist desc,
	c_count desc;
```

# Insights e Análises

1. ANÁLISE DE PROBLEMAS
   A consulta original apresenta potenciais gargalos de performance, principalmente devido à forma como as operações de junção, filtragem e agregação são processadas sem os índices adequados:

Filtro LIKE '%pattern%' não SARGable para B-tree: A condição o_comment not like '%special%requests%' na cláusula ON da junção é o principal ponto de lentidão. O padrão '%special%requests%' começa com um curinga (%), o que impede que um índice B-tree padrão na coluna o_comment seja utilizado de forma eficiente. O planejador do PostgreSQL não pode usar um índice B-tree para acelerar buscas com padrões LIKE que não são ancorados ao início da string (Conforme o manual do PostgreSQL, pág. 493). Isso resultará em um Seq Scan (varredura sequencial) completa na tabela orders para cada linha da tabela customer (ou para a tabela orders inteira se for um Hash Join), o que é extremamente custoso para tabelas grandes.
Ausência de índice em orders.o_custkey: A cláusula de junção c_custkey = o_custkey é fundamental. Embora c_custkey na tabela customer seja provavelmente uma chave primária (e, portanto, indexada), a coluna o_custkey na tabela orders (que é uma chave estrangeira) pode não ter um índice. A falta de um índice em orders.o_custkey pode levar a um Hash Join ou Merge Join menos eficiente, ou a um Nested Loop Join que exige varreduras sequenciais repetidas na tabela orders para cada cliente, aumentando drasticamente o custo de I/O (Conforme o manual do PostgreSQL, pág. 2399).
Múltiplas agregações e ordenação final: A consulta executa duas operações de agregação (GROUP BY c_custkey e GROUP BY c_count) e uma ordenação final (ORDER BY custdist desc, c_count desc). Cada uma dessas etapas pode ser intensiva em recursos (CPU e memória/disco) se os conjuntos de dados intermediários forem grandes, pois geralmente envolvem operações de classificação (Sort Aggregate) ou hashing (Hash Aggregate) (Conforme o manual do PostgreSQL, pág. 127). A ordenação final, em particular, provavelmente exigirá uma etapa de Sort explícita, pois as agregações anteriores eliminam qualquer ordem que pudesse ser fornecida por índices (Conforme o manual do PostgreSQL, pág. 497, 569). 2. CONSULTA OTIMIZADA
A estrutura lógica da consulta está correta para o resultado desejado. As otimizações de performance serão alcançadas através da adição de índices, sem a necessidade de reescrever o SQL.

select
c_count,
count(\*) as custdist
from
(
select
c_custkey,
count(o_orderkey) as c_count
from
customer left outer join orders on
c_custkey = o_custkey
and o_comment not like '%special%requests%'
group by
c_custkey
) as c_orders
group by
c_count
order by
custdist desc,
c_count desc; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
As otimizações para esta consulta se concentram na criação de índices que permitirão ao planejador do PostgreSQL executar as operações de junção e filtragem de forma muito mais eficiente.

Índices Recomendados:

Índice em orders.o_custkey:

Comando: CREATE INDEX idx_orders_o_custkey ON orders (o_custkey);
Explicação: Este índice é fundamental para otimizar a cláusula de junção c_custkey = o_custkey. Com este índice, o planejador poderá escolher um plano de junção mais eficiente, como um Nested Loop Join ou um Merge Join. Se customer for a tabela externa em um Nested Loop Join, para cada c_custkey, o índice idx_orders_o_custkey permitirá uma busca rápida pelas ordens correspondentes na tabela orders, evitando varreduras sequenciais completas. Isso reduzirá drasticamente o custo de I/O e o tempo de execução da junção (Conforme o manual do PostgreSQL, pág. 2399).
Índice GIN trigram em orders.o_comment:

Comando:
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_orders_o_comment_trgm ON orders USING GIN (o_comment gin_trgm_ops);
Explicação: A condição o_comment not like '%special%requests%' é o maior desafio de performance. Um índice B-tree padrão não é eficaz para padrões LIKE que começam com % (Conforme o manual do PostgreSQL, pág. 493). A extensão pg_trgm e um índice GIN (gin_trgm_ops) são projetados para acelerar buscas de texto com padrões LIKE '%pattern%' (Conforme o manual do PostgreSQL, pág. 2973, 2974).
Para a condição NOT LIKE, o planejador pode utilizar o índice GIN para identificar eficientemente as linhas que correspondem ao padrão '%special%requests%' através de um Bitmap Index Scan. Em seguida, essas linhas seriam excluídas do conjunto de resultados. Se o número de ordens que contêm "special requests" for relativamente pequeno, esta abordagem será muito mais rápida do que um Seq Scan completo na tabela orders, pois o índice permite filtrar um grande volume de dados sem ler todas as páginas da tabela.
Plano de Execução Estimado (com índices):

Subconsulta Interna (c_orders):

customer: O planejador provavelmente iniciará com um Seq Scan na tabela customer (assumindo que não há filtros na tabela customer em si).
Junção com orders: Para cada linha de customer, o planejador realizará uma busca de índice (Index Scan) na tabela orders usando idx_orders_o_custkey para encontrar as ordens correspondentes. Para cada ordem encontrada, a condição o_comment not like '%special%requests%' será avaliada. O índice idx_orders_o_comment_trgm pode ser usado para otimizar essa filtragem, possivelmente através de um Bitmap Index Scan para identificar e excluir as ordens que contêm o padrão. O tipo de junção mais provável será um Nested Loop Join (com customer como tabela externa) ou um Hash Join (se a tabela orders filtrada for grande o suficiente para justificar a construção de uma tabela hash).
Agregação por c_custkey: Os resultados da junção e filtragem serão então agregados por c_custkey. Esta etapa será realizada por um Hash Aggregate ou Sort Aggregate, dependendo do volume de dados e da memória disponível. Se a agregação paralela for habilitada e aplicável, o planejador pode utilizar Partial Aggregate e Finalize Aggregate (Conforme o manual do PostgreSQL, pág. 596).
Consulta Externa:

Agregação por c_count: Os resultados da subconsulta (clientes e suas contagens de ordens) serão agregados novamente por c_count. Esta será outra etapa de Hash Aggregate ou Sort Aggregate.
Ordenação Final: O conjunto de resultados final será ordenado por custdist DESC, c_count DESC. Como as agregações anteriores destroem qualquer ordem natural dos dados, esta etapa será um Sort explícito (Conforme o manual do PostgreSQL, pág. 497, 569).
Recomendações de Manutenção:

VACUUM ANALYZE: É crucial executar VACUUM ANALYZE regularmente nas tabelas customer e orders após a criação dos índices e após quaisquer operações significativas de modificação de dados (inserções, atualizações, exclusões). Isso garante que as estatísticas do planejador estejam atualizadas, permitindo que ele tome decisões informadas sobre os planos de execução mais eficientes.
REINDEX: Se as tabelas customer e orders sofrerem um alto volume de atualizações e exclusões, os índices podem se tornar "inchados" (bloated), o que pode degradar o desempenho. Um REINDEX periódico pode ser considerado para reconstruir os índices e otimizar seu uso de espaço em disco.

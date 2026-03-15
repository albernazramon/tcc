# Consulta Otimizada

```sql
-- Sugestão de índices para otimização:
-- É fundamental que as colunas de junção e filtro estejam indexadas.
-- Assumindo que o_orderkey é a chave primária de public.orders, ela já deve ter um índice.
-- CREATE INDEX IF NOT EXISTS ix_orders_orderkey ON public.orders (o_orderkey);
-- CREATE INDEX IF NOT EXISTS ix_lineitem_orderkey ON public.lineitem (l_orderkey);
-- CREATE INDEX IF NOT EXISTS ix_orders_orderstatus ON public.orders (o_orderstatus);
-- CREATE INDEX IF NOT EXISTS ix_lineitem_quantity ON public.lineitem (l_quantity);

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
    AND o.o_orderstatus IS DISTINCT FROM 'F'; -- Garante que não haja duplicatas de linhas já cobertas pela primeira parte
```

# Insights e Análises

ANÁLISE DE PROBLEMAS
A consulta original apresenta os seguintes problemas de performance no PostgreSQL:

Condição OR em WHERE entre tabelas unidas: A principal causa da lentidão é a condição OR (o.o_orderstatus = 'F' OR l.l_quantity > 40) que abrange colunas de duas tabelas diferentes (public.orders e public.lineitem) após uma operação JOIN. O otimizador do PostgreSQL tem dificuldade em utilizar índices de forma eficiente para essa condição combinada.
Quando uma condição OR envolve colunas de tabelas distintas que estão sendo unidas, o filtro é geralmente aplicado após a junção. Isso significa que o PostgreSQL pode precisar realizar uma junção completa (ou quase completa) das tabelas antes de poder descartar as linhas que não satisfazem a condição OR.
Mesmo que existam índices nas colunas o_orderstatus e l_quantity, o otimizador pode não conseguir usá-los para pré-filtrar eficientemente os dados antes da junção, ou para guiar a junção de forma otimizada para ambas as condições simultaneamente. Isso frequentemente resulta em Seq Scans (varreduras sequenciais completas) em uma ou ambas as tabelas, ou em um Hash Join caro, onde o filtro é aplicado tardiamente.
Falta de Índices Adequados: A ausência de índices nas colunas envolvidas na junção e nas condições de filtro é um fator crítico.
Junção: Sem índices em o.o_orderkey (na tabela orders) e l.l_orderkey (na tabela lineitem), a junção (o.o_orderkey = l.l_orderkey) pode recorrer a métodos menos eficientes como Hash Join (que exige varreduras completas para construir tabelas hash) ou Merge Join (que exige ordenação prévia se os dados não estiverem indexados/ordenados), em vez de um Nested Loop Join eficiente com Index Scans.
Filtro: Sem índices em o.o_orderstatus e l.l_quantity, mesmo que o otimizador pudesse aplicar os filtros mais cedo, ele teria que realizar Seq Scans nas tabelas para encontrar as linhas correspondentes.
Custo da Junção Intermediária: Se as tabelas orders e lineitem forem grandes, a junção completa antes da filtragem pode gerar um conjunto de resultados intermediário muito grande. Processar e filtrar esse grande volume de dados intermediários consome muitos recursos de CPU e memória, aumentando o tempo de execução da consulta.
CONSULTA OTIMIZADA
-- Sugestão de índices para otimização:
-- É fundamental que as colunas de junção e filtro estejam indexadas.
-- Assumindo que o_orderkey é a chave primária de public.orders, ela já deve ter um índice.
-- CREATE INDEX IF NOT EXISTS ix_orders_orderkey ON public.orders (o_orderkey);
-- CREATE INDEX IF NOT EXISTS ix_lineitem_orderkey ON public.lineitem (l_orderkey);
-- CREATE INDEX IF NOT EXISTS ix_orders_orderstatus ON public.orders (o_orderstatus);
-- CREATE INDEX IF NOT EXISTS ix_lineitem_quantity ON public.lineitem (l_quantity);

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
AND o.o_orderstatus IS DISTINCT FROM 'F'; -- Garante que não haja duplicatas de linhas já cobertas pela primeira parte
EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
Explicação das Mudanças:

A consulta original foi reescrita utilizando a cláusula UNION ALL para dividir a condição OR em duas subconsultas independentes. Esta técnica é conhecida como "desagregação de OR" e permite que o otimizador do PostgreSQL trate cada parte da condição de forma mais eficiente.

Primeira Subconsulta:

SELECT o.o_orderkey, o.o_orderdate, l.l_extendedprice
FROM public.orders o
JOIN public.lineitem l ON o.o_orderkey = l.l_orderkey
WHERE o.o_orderstatus = 'F'
Esta parte da consulta foca exclusivamente em pedidos com o_orderstatus = 'F'. Com um índice em o_orderstatus, o PostgreSQL pode rapidamente identificar os pedidos relevantes.

Segunda Subconsulta:

SELECT o.o_orderkey, o.o_orderdate, l.l_extendedprice
FROM public.orders o
JOIN public.lineitem l ON o.o_orderkey = l.l_orderkey
WHERE l.l_quantity > 40
AND o.o_orderstatus IS DISTINCT FROM 'F'
Esta parte foca em itens de linha com l_quantity > 40. A condição AND o.o_orderstatus IS DISTINCT FROM 'F' é crucial. Ela garante que apenas as linhas que não foram incluídas pela primeira subconsulta (ou seja, onde o.o_orderstatus não é 'F') sejam consideradas. Isso evita a duplicação de resultados que satisfazem ambas as condições simultaneamente, mantendo a semântica exata da consulta original com OR. IS DISTINCT FROM é preferível a <> para lidar corretamente com valores NULL em o_orderstatus.

Como o PostgreSQL Provavelmente Processará a Nova Consulta:

Consulta Original (sem índices):

Plano Estimado: O PostgreSQL provavelmente executaria um Seq Scan em public.orders e outro Seq Scan em public.lineitem. Em seguida, realizaria um Hash Join (ou Merge Join) para combinar as tabelas com base em o_orderkey = l.l_orderkey. Finalmente, aplicaria a condição o.o_orderstatus = 'F' OR l.l_quantity > 40 como um Filter no resultado já unido.
Impacto Previsto: Alto custo de I/O e CPU devido às varreduras completas e à junção de grandes volumes de dados antes da filtragem.
Consulta Otimizada (com índices sugeridos): Cada subconsulta será processada de forma independente e otimizada:

Para a Primeira Subconsulta (WHERE o.o_orderstatus = 'F'):

Plano Estimado:
Index Scan em public.orders: O PostgreSQL usaria o índice ix_orders_orderstatus para localizar rapidamente os o_orderkeys dos pedidos com o_orderstatus = 'F'.
Nested Loop Join com public.lineitem: Para cada o_orderkey encontrado, o otimizador faria um Index Scan no índice ix_lineitem_orderkey de public.lineitem para encontrar eficientemente todos os itens de linha correspondentes.
Impacto Previsto: Redução drástica de I/O e CPU. A filtragem é aplicada no início (Index Scan), e a junção é realizada em conjuntos de dados muito menores, transformando Seq Scans em Index Scans seletivos.
Para a Segunda Subconsulta (WHERE l.l_quantity > 40 AND o.o_orderstatus IS DISTINCT FROM 'F'):

Plano Estimado:
Index Scan em public.lineitem: O PostgreSQL usaria o índice ix_lineitem_quantity para localizar rapidamente os l_orderkeys dos itens de linha com l_quantity > 40.
Nested Loop Join com public.orders: Para cada l_orderkey encontrado, o otimizador faria um Index Scan no índice ix_orders_orderkey de public.orders para encontrar o pedido correspondente.
Filter: A condição o.o_orderstatus IS DISTINCT FROM 'F' seria aplicada como um filtro adicional sobre os resultados da junção.
Impacto Previsto: Similar à primeira subconsulta, com ganhos significativos de performance devido à filtragem inicial e junção eficiente.
Combinação (UNION ALL):

O UNION ALL simplesmente concatena os resultados das duas subconsultas. Esta é uma operação relativamente barata, pois não exige ordenação ou remoção de duplicatas (já que a segunda subconsulta foi projetada para não gerar duplicatas com a primeira).
Impacto Previsto: O custo total da consulta otimizada será a soma dos custos das duas subconsultas, que individualmente são muito mais eficientes do que a consulta original. A mudança de Seq Scan para Index Scan e a aplicação de filtros mais cedo no plano de execução resultarão em uma performance de alta performance.
Recomendações de Manutenção:

VACUUM ANALYZE Regular: É fundamental executar VACUUM ANALYZE regularmente nas tabelas public.orders e public.lineitem. Isso garante que as estatísticas do planejador de consultas estejam atualizadas e precisas, permitindo que o PostgreSQL escolha o plano de execução mais eficiente para as subconsultas e o UNION ALL. Estatísticas desatualizadas podem levar o otimizador a ignorar índices ou escolher planos subótimos.
Monitoramento de Índices: Monitore o uso e a saúde dos índices sugeridos. Verifique se estão sendo utilizados conforme o esperado e se não há fragmentação excessiva (embora menos comum no PostgreSQL do que em outros SGBDs). Se necessário, considere REINDEX para reconstruir índices.
Análise de EXPLAIN (ANALYZE, BUFFERS): Após a implementação dos índices e da consulta otimizada, execute EXPLAIN (ANALYZE, BUFFERS) na nova consulta para verificar o plano de execução real, os tempos de execução e o uso de recursos. Isso confirmará os ganhos de performance e ajudará a identificar quaisquer gargalos inesperados.
Tipos de Dados: Considere a conversão de o_orderdate e l_shipdate de character varying(50) para tipos de dados de data/hora (DATE ou TIMESTAMP). Isso otimiza o armazenamento, a indexação e as operações de data, além de garantir a validação de dados.
Chaves Primárias/Estrangeiras: Certifique-se de que o_orderkey seja definida como chave primária em public.orders e l_orderkey como chave estrangeira em public.lineitem referenciando orders. Isso não apenas impõe a integridade referencial, mas também cria índices automaticamente nas colunas de junção, que são cruciais para a performance.

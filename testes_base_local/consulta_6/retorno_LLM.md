# Consulta Otimizada

```sql
SELECT o_orderkey, o_orderpriority
FROM public.orders
WHERE o_orderpriority = '1-URGENT' OR o_orderstatus = 'O';
```

# Insights e Análises

ANÁLISE DE PROBLEMAS
Custo do Operador UNION: A consulta original utiliza o operador UNION, que por padrão realiza a eliminação de linhas duplicadas do conjunto de resultados. Conforme o manual do PostgreSQL (pág. 173.0 e pág. 2113.0), essa operação de eliminação de duplicatas exige um processo interno de ordenação ou hashing, que é computacionalmente intensivo e consome recursos significativos (CPU e I/O), especialmente em tabelas grandes ou com muitos resultados. Se a eliminação de duplicatas não for estritamente necessária, o uso de UNION ALL seria mais rápido, mas a semântica original exige a unicidade.
Múltiplas Varreduras Sequenciais (Seq Scan): Sem a presença de índices nas colunas o_orderpriority e o_orderstatus, o otimizador de consultas do PostgreSQL será forçado a realizar duas varreduras sequenciais completas (Seq Scan) na tabela public.orders, uma para cada subconsulta do UNION. Conforme o manual (pág. 573.0), um Seq Scan é o método de acesso padrão quando não há índices utilizáveis. Isso significa que a tabela inteira é lida do disco duas vezes, o que é extremamente ineficiente para tabelas de grande porte.
Ausência de Índices para Condições SARGable: As condições o_orderpriority = '1-URGENT' e o_orderstatus = 'O' são SARGable (Search Argumentable), o que significa que elas podem se beneficiar diretamente do uso de índices. A falta de índices impede o planejador de consultas de utilizar métodos de acesso mais eficientes, como Index Scan ou Bitmap Index Scan, que localizam rapidamente as linhas que satisfazem as condições WHERE sem precisar ler a tabela inteira (pág. 568.0).
CONSULTA OTIMIZADA
SELECT o_orderkey, o_orderpriority
FROM public.orders
WHERE o_orderpriority = '1-URGENT' OR o_orderstatus = 'O';
EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
Explicação das Mudanças: A principal mudança foi a substituição do operador UNION por uma única instrução SELECT utilizando a condição OR na cláusula WHERE. Esta reescrita mantém a semântica original da consulta, que é retornar pares únicos de (o_orderkey, o_orderpriority) que satisfaçam pelo menos uma das condições. Ao usar OR, qualquer linha da tabela orders que atenda a o_orderpriority = '1-URGENT' ou o_orderstatus = 'O' será selecionada uma única vez, eliminando a necessidade de uma etapa explícita e custosa de eliminação de duplicatas que o UNION impõe (pág. 173.0, pág. 2113.0).

Plano de Execução Estimado e Impacto:

Consulta Original: O plano de execução para a consulta original, sem índices, envolveria:

Dois Seq Scan na tabela public.orders, um para cada subconsulta.
Um Append para combinar os resultados das duas subconsultas.
Uma operação de HashAggregate ou Sort para remover as duplicatas, o que adiciona um custo significativo de CPU e memória. Este plano é ineficiente devido às múltiplas varreduras completas da tabela e ao custo da eliminação de duplicatas.
Consulta Otimizada: Com a consulta reescrita e a criação dos índices recomendados, o PostgreSQL provavelmente adotará um plano de execução mais eficiente:

Bitmap Index Scan: O planejador executará um Bitmap Index Scan em idx_orders_orderpriority para encontrar as linhas onde o_orderpriority = '1-URGENT'.
Bitmap Index Scan: Simultaneamente, executará outro Bitmap Index Scan em idx_orders_orderstatus para encontrar as linhas onde o_orderstatus = 'O'.
Combinação de Bitmaps: Os resultados desses Bitmap Index Scans (que são bitmaps de localização das tuplas) serão combinados usando uma operação OR (pág. 497.0, pág. 498.0, pág. 576.0). Isso permite que o sistema identifique todas as linhas que satisfazem qualquer uma das condições de forma eficiente.
Bitmap Heap Scan: Finalmente, um Bitmap Heap Scan será realizado para buscar as linhas reais da tabela public.orders com base no bitmap combinado. Este método acessa as páginas da tabela de forma mais otimizada, visitando cada página apenas uma vez, mesmo que contenha várias tuplas correspondentes (pág. 568.0). Este plano evita múltiplas varreduras sequenciais e a etapa de eliminação de duplicatas, resultando em uma performance significativamente superior, especialmente para tabelas grandes.
Recomendações de Manutenção:

Criação de Índices: Para que a consulta otimizada utilize o Bitmap Heap Scan e Bitmap Index Scan, é fundamental criar índices nas colunas envolvidas nas condições WHERE. Recomenda-se a criação de índices B-tree separados para cada coluna, permitindo que o planejador combine os resultados dos índices para a condição OR (pág. 2831.0).
CREATE INDEX idx_orders_orderpriority ON public.orders (o_orderpriority);
CREATE INDEX idx_orders_orderstatus ON public.orders (o_orderstatus);
ANALYZE: Após a criação dos índices e periodicamente, execute ANALYZE public.orders; para garantir que o otimizador de consultas tenha estatísticas atualizadas sobre a distribuição dos dados na tabela e nos novos índices. Estatísticas precisas são cruciais para que o planejador escolha o plano de execução mais eficiente.
VACUUM: Mantenha a tabela public.orders e seus índices otimizados através da execução regular de VACUUM (ou configure o autovacuum). Isso ajuda a remover tuplas mortas, recuperar espaço em disco e manter a eficiência dos índices, especialmente após operações de INSERT, UPDATE ou DELETE.

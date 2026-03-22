# Consulta Otimizada

```sql
SELECT
    c_name,
    c_acctbal
FROM
    public.customer
WHERE
    UPPER(c_name) LIKE 'CUSTOMER#000000001%';
```

# Insights e Análises

1. ANÁLISE DE PROBLEMAS
   A consulta original é lenta principalmente devido à aplicação da função UPPER() na coluna c_name dentro da cláusula WHERE. Esta prática torna a condição não-SARGable.

Não-SARGability da Função UPPER(): Ao aplicar UPPER(c_name), o PostgreSQL é forçado a calcular o valor em maiúsculas para cada linha da tabela public.customer antes de poder comparar com o padrão LIKE. Isso impede o uso direto de qualquer índice B-tree existente na coluna c_name. O otimizador de consultas não consegue usar um índice para pular diretamente para as linhas relevantes, resultando em um Seq Scan (varredura sequencial completa da tabela) (Conforme o manual do PostgreSQL (pág. 573)). Um Seq Scan lê todas as páginas da tabela, o que é ineficiente para tabelas grandes.
Custo de Processamento por Linha: Além do Seq Scan, a função UPPER() precisa ser executada para cada linha, adicionando um custo de CPU significativo ao processamento da consulta.
LIKE com Prefixo Constante: Embora o operador LIKE com um padrão ancorado à esquerda ('prefix%') possa, em teoria, utilizar um índice B-tree (Conforme o manual do PostgreSQL (pág. 493)), a presença da função UPPER() anula essa otimização. Se a função não estivesse presente, um índice B-tree em c_name poderia ser usado para acelerar a busca. 2. CONSULTA OTIMIZADA
A consulta otimizada mantém a semântica original, mas será acelerada pela criação de um índice apropriado, conforme detalhado na seção de explicação técnica.

SELECT
c_name,
c_acctbal
FROM
public.customer
WHERE
UPPER(c_name) LIKE 'CUSTOMER#000000001%'; 3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO
As mudanças para otimizar esta consulta não envolvem a reescrita do SQL em si, mas sim a criação de um índice estratégico que permite ao PostgreSQL processar a condição WHERE de forma eficiente.

Mudanças Feitas: A principal "mudança" é a recomendação de um índice de expressão. A consulta SQL permanece a mesma porque a função UPPER() é intrínseca à lógica de negócios desejada (busca case-insensitive).

Recomendação de Índice: Para otimizar a consulta, é essencial criar um índice de expressão na coluna c_name que precalcule o valor em maiúsculas. Isso torna a condição UPPER(c_name) LIKE '...' SARGable.

CREATE INDEX idx_customer_c_name_upper ON public.customer (UPPER(c_name) varchar_pattern_ops);
UPPER(c_name): Cria um índice sobre o resultado da função UPPER() aplicada à coluna c_name. Isso significa que o índice armazenará os nomes dos clientes já em maiúsculas.
varchar_pattern_ops: Esta classe de operador é crucial. Ela permite que o índice B-tree seja usado eficientemente para operadores de correspondência de padrões como LIKE (Conforme o manual do PostgreSQL (pág. 505)). É especialmente útil se o banco de dados não estiver usando a locale "C", pois garante que as comparações de padrão sejam estritamente caractere por caractere, o que é necessário para o otimizador usar o índice com LIKE 'prefix%'.
Como o PostgreSQL Processará a Nova Consulta (com o Índice):

Consulta Original (sem o índice): O PostgreSQL executaria um Seq Scan (varredura sequencial) na tabela public.customer. Para cada linha, ele aplicaria a função UPPER() a c_name e, em seguida, compararia o resultado com o padrão LIKE. Isso é ineficiente, pois exige a leitura de todas as páginas da tabela e o cálculo da função para cada linha (Conforme o manual do PostgreSQL (pág. 573)).

Consulta Otimizada (com o índice idx_customer_c_name_upper):

Bitmap Index Scan: O otimizador de consultas agora pode usar o índice idx_customer_c_name_upper. Ele realizará um Bitmap Index Scan no índice para encontrar rapidamente os TIDs (Tuple IDs) das linhas onde UPPER(c_name) corresponde ao padrão 'CUSTOMER#000000001%'. O índice já contém os valores em maiúsculas, permitindo uma busca direta e eficiente.
Bitmap Heap Scan: Após identificar os TIDs correspondentes no índice, o PostgreSQL realizará um Bitmap Heap Scan na tabela public.customer. Este passo recupera as linhas reais da tabela usando os TIDs obtidos do índice. Este método é muito mais eficiente do que um Seq Scan porque evita a leitura de páginas de dados irrelevantes, acessando apenas as páginas que contêm as linhas correspondentes (Conforme o manual do PostgreSQL (pág. 568)).
Impacto Previsto: A criação do índice de expressão transformará um provável Seq Scan em um Bitmap Index Scan seguido por um Bitmap Heap Scan. Isso resultará em uma redução drástica no tempo de execução da consulta, especialmente em tabelas grandes, pois o número de blocos de disco a serem lidos será significativamente menor. A consulta passará de uma operação I/O-bound e CPU-bound (devido ao UPPER() em cada linha) para uma operação I/O-bound mais eficiente, focada apenas nos dados relevantes.

Recomendações de Manutenção:

VACUUM: É crucial executar VACUUM regularmente (ou confiar no autovacuum) na tabela public.customer. Isso ajuda a recuperar espaço de tuplas mortas e mantém a tabela e seus índices eficientes, evitando o inchaço (bloat) e garantindo que os índices permaneçam compactos e rápidos.
ANALYZE: Certifique-se de que ANALYZE (ou autoanalyze) seja executado periodicamente na tabela public.customer. Isso atualiza as estatísticas de distribuição de dados, que são vitais para o otimizador de consultas escolher o plano de execução mais eficiente. Estatísticas desatualizadas podem levar o otimizador a escolher um plano subótimo, mesmo com o índice presente.
